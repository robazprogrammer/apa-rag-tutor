const form = document.querySelector("#question-form");
const question = document.querySelector("#question");
const submit = form.querySelector(".submit");
const clearQuestion = document.querySelector("#clear-question");
const saveResults = document.querySelector("#save-results");
const submittedQuestion = document.querySelector("#submitted-question");
const answerSection = document.querySelector("#answer-section");
const answer = document.querySelector("#answer");
const sourceSection = document.querySelector("#sources-section");
const sources = document.querySelector("#sources");
const status = document.querySelector("#status");

const BASIS_CLASS = {
  "APA guide": "basis-guide",
  "assignment directions": "basis-directions",
  "not covered": "basis-none",
};

function renderPart(part) {
  const row = document.createElement("li");
  row.className = "part";
  if (part.ask) {
    const ask = document.createElement("strong");
    ask.textContent = part.ask;
    row.append(ask);
  }
  const text = document.createElement("p");
  text.textContent = part.answer;
  const basis = document.createElement("p");
  basis.className = "meta";
  const label = document.createElement("span");
  if (part.unverified) {
    label.className = "basis basis-none";
    label.textContent = "APA guide claim with no supporting passage. Check below";
  } else {
    label.className = `basis ${BASIS_CLASS[part.basis] || "basis-none"}`;
    label.textContent = part.basis === "not covered" ? "Not covered by the guide" : `From the ${part.basis}`;
  }
  basis.append(label);
  // Link each cited number to its passage so students can check the claim.
  for (const id of part.source_ids) {
    const link = document.createElement("a");
    link.href = `#source-${id}`;
    link.textContent = `[${id}]`;
    basis.append(" ", link);
  }
  if (part.matched_by_text) {
    const how = document.createElement("small");
    how.textContent = " matched by wording";
    how.title = "The AI gave no passage number, so the tutor matched the answer's wording to this passage.";
    basis.append(how);
  }
  row.append(text, basis);
  return row;
}

function renderSource(source, index) {
  const row = document.createElement("li");
  row.id = `source-${index + 1}`;
  const heading = document.createElement("strong");
  heading.textContent = source.heading || source.source;
  const metadata = document.createElement("p");
  metadata.className = "meta";
  metadata.textContent = source.page ? `${source.source} · page ${source.page}` : source.source;
  const passage = document.createElement("p");
  passage.textContent = source.text;
  row.append(heading, metadata, passage);
  if (source.url.startsWith("https://")) {
    const link = document.createElement("a");
    link.href = source.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Read the source";
    row.append(link);
  }
  return row;
}

for (const button of document.querySelectorAll("[data-question]")) {
  button.addEventListener("click", () => {
    question.value = button.dataset.question;
    question.focus();
  });
}

form.addEventListener("change", () => {
  submit.textContent = form.elements.mode.value === "ai" ? "Ask the tutor" : "Search the guide";
});

clearQuestion.addEventListener("click", () => {
  question.value = "";
  question.focus();
});

saveResults.addEventListener("click", () => window.print());

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  if (!data.question.trim() || submit.disabled) return;
  submit.disabled = true;
  status.textContent = data.mode === "ai" ? "Searching and asking the local model…" : "Searching…";
  answerSection.hidden = true;
  sourceSection.hidden = true;
  saveResults.hidden = true;
  submittedQuestion.textContent = "";
  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    answer.replaceChildren(...result.parts.map(renderPart));
    answerSection.hidden = !result.parts.length;
    sources.replaceChildren(...result.sources.map(renderSource));
    sourceSection.hidden = !result.sources.length;
    if (result.parts.length || result.sources.length) {
      submittedQuestion.textContent = data.question.trim();
      saveResults.hidden = false;
    }
    const count = result.sources.length;
    status.textContent = result.notes.join("\n") || `Found ${count} guide passage${count === 1 ? "" : "s"}.`;
  } catch (error) {
    status.textContent = error.message || "The tutor could not complete the request.";
  } finally {
    submit.disabled = false;
  }
});

// ---------- Citation builder (plain Python rules on the server, no AI) ----------
const citeForm = document.querySelector("#cite-form");
const citeStatus = document.querySelector("#cite-status");
const citeResult = document.querySelector("#cite-result");
const citeNotes = document.querySelector("#cite-notes");

citeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  citeStatus.textContent = "";
  citeResult.hidden = true;
  try {
    const response = await fetch("/cite", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(Object.fromEntries(new FormData(citeForm))),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    document.querySelector("#cite-parenthetical").textContent = result.parenthetical;
    document.querySelector("#cite-narrative").textContent = result.narrative;
    document.querySelector("#cite-placement").textContent = result.placement;
    citeNotes.replaceChildren(...result.notes.map((note) => {
      const item = document.createElement("li");
      item.textContent = note;
      return item;
    }));
    document.querySelector("#cite-notes-label").hidden = !result.notes.length;
    citeNotes.parentElement.hidden = !result.notes.length;
    citeResult.hidden = false;
  } catch (error) {
    citeStatus.textContent = error.message || "The citation could not be built.";
  }
});

for (const button of document.querySelectorAll("[data-copy]")) {
  button.addEventListener("click", async () => {
    const text = document.querySelector(`#${button.dataset.copy}`).textContent;
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Select and copy";
    }
    setTimeout(() => { button.textContent = "Copy"; }, 1500);
  });
}
