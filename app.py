"""Run with python app.py and use the tutor in your browser."""

import argparse
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import webbrowser

from citations import CitationError, build_citation
from rag import LocalAIError, generate, load_guides, retrieve_for_question

ROOT = Path(__file__).resolve().parent
STATIC = {
    "/": ("index.html", "text/html"),
    "/style.css": ("style.css", "text/css"),
    "/app.js": ("app.js", "text/javascript"),
}


class TutorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Student questions are never written to an application log.
        pass

    def send_content(self, status, body, media_type):
        self.send_response(status)
        self.send_header("Content-Type", f"{media_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, data):
        self.send_content(status, json.dumps(data).encode("utf-8"), "application/json")

    def allowed_host(self):
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def do_GET(self):
        if not self.allowed_host() or self.path not in STATIC:
            self.send_error(404)
            return
        name, media_type = STATIC[self.path]
        self.send_content(200, (ROOT / "web" / name).read_bytes(), media_type)

    def read_json(self):
        """Apply the same safety checks to every POST, then return the JSON body."""
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if not self.allowed_host() or self.headers.get("Origin") != origin:
            self.send_json(403, {"error": "Open the tutor using its local browser address."})
            return None
        if self.headers.get_content_type() != "application/json":
            self.send_json(415, {"error": "Expected a JSON request."})
            return None
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 25_000:
                raise ValueError
            request = json.loads(self.rfile.read(length))
            if not isinstance(request, dict):
                raise ValueError
            return request
        except ValueError:
            self.send_json(400, {"error": "The request could not be read."})
            return None

    def do_POST(self):
        if self.path == "/ask":
            self.handle_ask()
        elif self.path == "/cite":
            self.handle_cite()
        else:
            self.send_json(404, {"error": "Not found."})

    def handle_ask(self):
        request = self.read_json()
        if request is None:
            return
        try:
            question = request["question"].strip()
            directions = request.get("directions", "").strip()
            mode = request["mode"]
            if not 0 < len(question) <= 500 or len(directions) > 2000 or mode not in ("guide", "ai"):
                raise ValueError
        except (ValueError, KeyError, AttributeError, TypeError):
            self.send_json(400, {"error": "Enter a question of 1 to 500 characters and up to 2,000 characters of directions."})
            return

        passages, notes = load_guides(ROOT / "docs")
        # Each part of a multi-part question gets its own search, so no part is left without evidence.
        matches = retrieve_for_question(question, passages, limit=4)
        parts = []
        if mode == "ai" and matches:
            try:
                parts = generate(question, directions, matches)
            except LocalAIError as error:
                notes.append(str(error))
        if not matches:
            notes.append("No matching passages. Try a term like “title page,” “paraphrase,” or “hanging indent.”")
        self.send_json(200, {
            "parts": parts, "notes": notes, "sources": [asdict(item) for item in matches],
        })

    def handle_cite(self):
        request = self.read_json()
        if request is None:
            return
        try:
            words = str(request.get("quote_words", "")).strip()
            citation = build_citation(
                str(request.get("authors", ""))[:2500],
                str(request.get("year", "")),
                str(request.get("locator_kind", "none")),
                str(request.get("locator", "")),
                int(words) if words else None,
            )
        except CitationError as error:
            self.send_json(400, {"error": str(error)})
            return
        except ValueError:
            self.send_json(400, {"error": "Enter the quote length as a whole number of words, or leave it blank."})
            return
        self.send_json(200, asdict(citation))


def main():
    parser = argparse.ArgumentParser(description="Run the local APA RAG Tutor.")
    parser.add_argument("--port", type=int, default=8765, help="Local browser port (default: 8765).")
    parser.add_argument("--no-browser", action="store_true", help="Print the URL without opening a tab.")
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), TutorHandler)
    except OSError as error:
        parser.exit(1, f"Could not start the tutor: {error}. Try --port 8766.\n")
    with server:
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"APA RAG Tutor is running at {url}. Press Ctrl+C to stop.", flush=True)
        if not args.no_browser:
            threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nTutor stopped.")


if __name__ == "__main__":
    main()
