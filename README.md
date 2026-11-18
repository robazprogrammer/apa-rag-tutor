# APA RAG Tutor

An APA 7 formatting tutor that runs on your computer and opens in your browser. It comes with a searchable guide covering student papers, discussion posts, in-text citations, and reference lists. The starter guide is written in original language and links to official APA Style resources.

## Before you run the tutor

1. Unzip the project folder and put it on your Desktop.
2. Install [Python 3.10 or newer](https://www.python.org/downloads/) if needed.
3. If you plan to use **Ask the local AI**, complete the Ollama setup below before launching the tutor. If you only want **Search the guide**, skip to **Launch the tutor**.

### Set up Ollama for AI answers

1. Download and install [Ollama](https://ollama.com/download) as a desktop app. On Windows, select **Download manually** and run the installer. No `pip` command is needed.
2. Open Ollama and leave it running in the background. On Windows, you can open it from the Start menu.
3. Open a new terminal (PowerShell on Windows) and download the model the tutor uses. This is a one-time download of about 2 GB.

   ```sh
   ollama pull llama3.2:3b
   ```

4. Wait for the download to finish, then launch the tutor.

Ollama runs this model on your computer without an account, API key, or paid subscription. A GPU is optional, and answers can take longer on a CPU. The tutor sends your questions, directions, and retrieved passages only to Ollama on your computer, and it does not save your questions.

## Launch the tutor

1. On Windows, double-click **Start_Tutor.bat**. You can also run `py -3 app.py` or `python app.py` from the project folder. On macOS or Linux, open a terminal in the project folder and run:

   ```sh
   python3 app.py
   ```

2. If the browser tab does not open, visit [http://127.0.0.1:8765](http://127.0.0.1:8765). Keep the terminal running while you use the tutor.
3. Select **Search the guide** to find passages with Python alone, or select **Ask the local AI** for a generated answer. In AI mode, you can also paste assignment-specific directions into the optional field.

Guide search works offline with Python's standard library. Opening the linked sources requires internet access. If the tutor says **Open Ollama and try again**, start Ollama and retry from the same browser tab. Press Ctrl+C in the tutor's terminal to close the tutor. Ollama runs separately.

### Try it in class

| Ask | Look for |
| --- | --- |
| Do I need a page number when I paraphrase? | A numbered passage about paraphrasing and page locators |
| How do I cite an article with three authors? | An example using et al. in an in-text citation |
| Does my Canvas discussion post need a title page? | Guidance about the assignment prompt. In AI mode, try adding “Use APA citations and references. No title page required.” |

In AI mode, the tutor answers each part of the question separately and labels where each part comes from: **From the APA guide** (with passage numbers you can click), **From the assignment directions**, or **Not covered by the guide**. Click each number to jump to its passage and check that it supports the answer. A part labeled "From the APA guide" with no supporting passage is shown as **Not covered by the guide**. Local generation can take longer, especially on the first question. For a quick lookup, use **Search the guide**. If Ollama cannot return a usable answer, the guide passages still appear below.

### Citation builder (no AI)

Below the results, the **Citation builder** makes exact APA 7 in-text citations with plain Python rules, so it never needs Ollama. Enter the author surnames (separated by commas), the year, an optional page, paragraph, or timestamp, and the quote length in words. Leave the length blank for a paraphrase. It returns the parenthetical and narrative citations with **Copy** buttons. It also says whether a quote of that length belongs in quotation marks or a block quote. Small AI models often get citation details wrong, so citations are handled by code and the AI is used for explanations.

Use **Clear question** to empty the question box while keeping the current result on screen. **Save results as PDF** opens your browser's print dialog. Choose **Save as PDF** or **Microsoft Print to PDF** as the destination. The PDF includes the submitted question, any AI answer, and the retrieved passages with their source links.

## Read or modify the code

- `docs/APA_7_Student_Guide.md` is the bundled knowledge base. Add your own permitted `.md` and `.txt` files under `docs/`. Changes are picked up on the next question.
- `rag.py` splits guides into passages and ranks them with BM25 keyword retrieval. It searches each part of a multi-part question separately, drops weak matches, and optionally sends the top passages to local Ollama for generation. It checks every AI answer part before it is shown.
- `citations.py` builds in-text citations with fixed APA rules (one, two, or three or more authors, page ranges, paragraphs, timestamps, n.d.). Run all tests (citations and retrieval) with `python -m unittest`.
- `app.py` serves the browser interface and delivers answers, evidence, and citations. The HTML, CSS, and JavaScript are in `web/`.
- For optional text-based PDF support, run `python -m pip install pypdf`, or use `python3` on macOS or Linux. Download permitted APA PDFs from the source links and put them in `docs/`. PDFs receive page numbers in the results. Scanned PDFs require a text layer.

To share on GitHub, upload the extracted folder contents, including `docs/` and `web/`. The app is designed for each student to run locally. Keep downloaded PDFs, private course materials, and student work out of the repo. The bundled guide and code are enough to run the project.

See `CHANGELOG.md` for what changed from the base version and why.

This is an independent classroom project. For a particular assignment, apply your instructor's directions.
