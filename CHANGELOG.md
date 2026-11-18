# Changelog

## Version 3: fixing the search step

A test question about a two-author paraphrase and a webpage with no date exposed a retrieval failure. The model never received the in-text citation or paraphrase passages. It answered from memory, cited an unrelated passage, and told the student page numbers were needed for a paraphrase. Fixing the model wouldn't help, because the evidence never reached it.

| Problem | Fix |
|---|---|
| One search over a multi-part question let its loudest topic ("journal article") crowd out the rest | **Each question and statement gets its own search** (`retrieve_for_question`). Its best passage goes first, then whole-question matches fill the remaining slots. |
| Students write "parenthetical"; the guide never did | The guide's in-text section now uses **"parenthetical" and "narrative"** |
| "page numbers" didn't match "page number" | Added missing **plural forms** to the word list |
| "Do I need a title page?" matched the *headings* passage ("title case") | A small bonus when a **two-word phrase** like "title page" appears in a heading |
| A one-line guide intro competed with real guidance | Passages under **20 words** are skipped |
| The model described reference entries when asked for in-text citations | The instructions now separate **in-text citations from reference entries**, and require yes/no answers to give the rule as the reason |
| The AI saw at most 3 passages, which cut the paraphrase passage | Back to **4 passages** (about 1,300 prompt tokens, well within the 4,096 context) |

`test_retrieval.py` now holds the class test questions. It checks that the search step finds every passage a correct answer needs: **8 of 8 pass**, versus 1 test question missing passages before. Run it with `python -m unittest`.

## Version 2: making a 3B local model trustworthy without a bigger model

The base version used one AI-written paragraph and one list of cited passages. Testing with `llama3.2:3b` showed three problems: the model skipped parts of multi-part questions, copied guide text instead of applying it to the student's details, and often listed no citations. Each fix below costs no extra memory.

| Problem seen in testing | Fix |
|---|---|
| Skipped parts of multi-part questions | The answer schema requires **one part per sub-question**. Each part is labeled *From the APA guide*, *From the assignment directions*, or *Not covered by the guide*. |
| Wrong or invented citation formats | A **citation builder** (`citations.py`) formats in-text citations with fixed rules and unit tests. No AI is involved. |
| Copied passages instead of applying them | The instructions include **one worked example** showing a rule applied to a different student's details. |
| Cited no passages | The schema asks for **passage IDs before the answer**. If the model still cites none, code **matches the answer's wording** to a passage and labels it *matched by wording*. |
| A claim labeled as from the guide with nothing behind it | Shown as **"APA guide claim with no supporting passage"**. It is never hidden or relabeled as covered. |
| Off-topic passages in the prompt | Retrieval **drops passages scoring under 50% of the best match**. The AI receives at most 3 passages. |
| Long answers broke the JSON | The answer limit was raised to 700 tokens. A cut-off answer gives a clear "ask one or two things at a time" message. |
| Crash when `docs/` was missing | Shows a clear message instead. |

Unchanged: the model runs locally through Ollama (free, about 2 GB), guide search runs on Python alone, and the server keeps its local-only safety checks.

## Limits and next upgrades

What three versions showed: the search step and the citation builder are reliable and easy to test. A 3-billion-parameter local model is the weak link. Even with a fixed output format, a worked example, and code checks, it can copy instead of apply, give weak reasons, and cite passages that don't support its answer. A larger hosted model handles APA questions better today, but costs money and sends questions off the student's computer.

Upgrades that would help, roughly in order of value:

1. **A larger model** where hardware or budget allows. The code needs only `MODEL` changed for another Ollama model, or `generate()` swapped for a hosted API.
2. **Embedding or hybrid search** so synonyms match without hand-made word lists.
3. **Checking that each passage supports its claim** (an entailment model) instead of word overlap, which can't tell "supports" from "shares words with."
4. **Answer-level tests**: expected answers for the class questions, scored automatically against a real model.
5. **More guide coverage**: more reference types, heading levels 4 and 5, tables and figures, and reference list examples.
6. **Follow-up questions and streamed answers** for a better chat experience.
