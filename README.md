# 💸 SpendWise

**An intelligent personal-finance assistant using prompt engineering and automated prompt optimisation.**
Course: Prompt Engineering and Optimisation for Generative AI · Team of 4

> Core question: *Do carefully designed and automatically optimised prompts produce more accurate, consistent and
> useful expense categorisation and explanations than a basic prompt?*

---

## 1. Run it (2 minutes)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501. With no API key it runs on the **offline simulator**, so the demo works with no
internet. For real results, pick a backend in the sidebar and paste a key:

| Backend | Get a key | Default model (editable in sidebar) |
|---|---|---|
| Google Gemini | aistudio.google.com → Get API key (free tier) | `gemini-3.8-flash` (auto-falls back to an available Flash model) |
| Groq (OpenAI-compatible, free tier) | console.groq.com | `llama-3.3-70b-versatile` |
| Anthropic Claude | console.anthropic.com | `claude-haiku-5-5` |

Or set environment variables before launching: `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` (+ `OPENAI_BASE_URL`).
If a default model name has been retired, type the current one in the sidebar's **Model** box.

### ⚠️ Before presenting: produce real numbers (~5 min)

The results already in `results/` come from the **offline simulator**, a rule-based stand-in that only reads the
prompt text. They prove the pipeline works. **They are not LLM results and must not be presented as such.**

```bash
export GEMINI_API_KEY=your_key        # Windows PowerShell:  $env:GEMINI_API_KEY="your_key"
python evaluate.py --backend gemini
```

This runs all 6 prompt arms plus both optimisers (~40–60 API calls, cached in `results/llm_cache.json`) and writes
`results/eval_gemini_<model>.json`. The **Prompt Lab** page picks it up automatically. You can also press
**▶ Run evaluation** inside the Prompt Lab.

Run the tests with `python -m pytest -q tests`.

---

## 2. What the app does

| Page | Feature (plan §5) | Prompt-engineering role |
|---|---|---|
| 🏠 Overview | Totals, category donut, monthly stacked bars, spending pace, top merchants | None. Pure pandas |
| 🏷️ Categorise | Every transaction labelled, confidence bar, *needs review* flag, **editable** categories | Selected strategy → JSON → Pydantic → repair retry |
| 💬 Ask SpendWise | Natural-language questions, with a full "prompt chain trace" | Route (LLM) → compute (Python) → explain (LLM) → grounding check |
| 🎯 Budget Coach | Budget/goal input, gauge, ≤3 suggestions with estimated savings | Constrained, grounded JSON prompt + Python guard-rails |
| 📄 Monthly Report | Headline, observations, next steps, MD/JSON download | Prompt chain → validated `MonthlyReport` schema |
| 🧪 Prompt Lab | Experiment results: accuracy, F1, JSON validity, cost, confusion matrix, optimiser curves, error browser | The research core (RQ1–RQ4) |
| 🧭 How it works | Architecture + RQ map + safety | |

## 3. Project structure

```
app.py                     Streamlit UI
evaluate.py                CLI: run the experiment
spendwise/
  data.py                  CSV import, column auto-mapping, row validation
  analytics.py             ALL arithmetic (pandas)
  prompts.py               Prompt library: every prompt, versioned and documented
  llm.py                   Gemini / Claude / OpenAI-compatible backends, cache, retries, offline simulator
  categorizer.py           Batched categorisation, strict + lenient parsing, repair retry
  assistant.py             Ask / budget / report chains + grounding checker
  optimizer.py             Arm C (DSPy-style bootstrap demos) and Arm D (TextGrad-style feedback rules)
  evaluation.py            Metrics on the held-out test split
  schemas.py               Pydantic output schemas
  ui.py                    Theme, CSS, chart template
data/
  generate_dataset.py      Reproducible synthetic data (seeded)
  labelled_transactions.csv  201 rows · 8 categories · 141 dev / 60 test (stratified) · 34 ambiguous
  sample_expenses.csv      3 months of student spending for the demo
results/                   eval_*.json/csv, optimized_prompts_*.json
tests/                     pytest
```

## 4. Experiment design

| Arm | Prompt | Technique |
|---|---|---|
| — | `zero_shot_plain` | Zero-shot, free-text output (scraped with regex) |
| — | `zero_shot_json` | Zero-shot + JSON schema |
| **A** | `role_guided` | Role + category guide + ambiguity rules + JSON (**best manual prompt**) |
| **B** | `few_shot` | A + 16 balanced labelled examples from the dev split |
| **C** | `optimized_bootstrap` | Auto-selected demos: base prompt run on dev-train, misclassified "hard" cases bootstrapped into 4 candidate demo sets, best kept by dev-validation accuracy (DSPy `BootstrapFewShotWithRandomSearch` idea) |
| **D** | `optimized_textgrad` | The LLM reads its own dev errors and writes correction rules ("textual gradients"). A rule is kept only if dev-validation accuracy does not drop (TextGrad idea) |

**Leakage control:** optimisers and few-shot examples use only `split == dev`. The 60-row test split is used once,
for the final scores. Dev is itself split into dev-train and dev-validation for the optimisers.

**Metrics:** accuracy, macro-F1, accuracy on ambiguous merchants, strict JSON validity (first response parses
against the schema), usable-output rate, review-flag rate, share of errors caught by the review flag, LLM calls,
tokens per transaction, latency.

**Cost control:** transactions go in batches of 20 per call, responses are cached on disk, and failed calls are
retried with backoff.

**Implementation note:** C and D are compact re-implementations of the DSPy and TextGrad *ideas*, so they work
with any backend and run on free tiers. They are not the actual libraries. Say this plainly if asked (plan §14 allows it).

## 5. Reliability and safety (plan §9)

* Python computes every number. The LLM only classifies and explains.
* **Grounding check:** every ₹ amount and % in an answer or report must match a number Python computed (within
  rounding). Otherwise a red ⚠ badge lists the unsupported figures (RQ4).
* Every structured output is validated by Pydantic, with one repair retry that feeds the validation error back.
* Budget guard-rail: a suggested saving can never exceed what is actually spent in that category.
* Ambiguous or unknown merchants go to low confidence + `needs_review`, and the user can correct any label.
* Synthetic data only. No bank logins, no account numbers. Uploads stay in session memory. API keys are never written to disk.
* All advice is labelled as educational guidance, not financial advice.

## 6. Team ownership (plan §11)

| Member | Owns in this codebase | Demo segment |
|---|---|---|
| P1 Data & analytics | `data.py`, `analytics.py`, `data/generate_dataset.py` | Upload + Overview |
| P2 Prompt engineering | `prompts.py`, `optimizer.py`, `llm.py` | Categorise + prompt viewer, optimiser curves |
| P3 Evaluation & reliability | `evaluation.py`, `schemas.py`, grounding check, `tests/` | Prompt Lab results |
| P4 Application & integration | `app.py`, `ui.py`, `assistant.py` | Ask SpendWise, Budget Coach, Report |

## 7. Suggested 6-minute demo

1. **Overview** (P1): "Here are 3 months of a student's spending. Every number on this page comes from pandas."
2. **Categorise** (P2): switch strategy from `zero_shot_plain` → `few_shot` → `optimized_textgrad` and watch the flagged count change. Open "See the exact prompt". Fix one flagged label by hand.
3. **Ask SpendWise** (P4): ask "Compare October with the previous month", then open the *prompt chain trace* and point at the ✓ Grounded badge. Then ask "Should I invest in crypto?" and show that it refuses.
4. **Budget Coach** (P4): set the budget below the average, generate suggestions, and point out the guard-rail and the missing-info notes.
5. **Prompt Lab** (P3): walk through the bar chart (RQ1/RQ3), the JSON validity bars (RQ2), the cost scatter, the confusion matrix, and the error browser.
6. Close with the pitch from plan §16.

## 8. Viva answers (plan §16)

1. **Why is this a prompt-engineering project and not just an expense tracker?** The tracker is only the test bed.
   The deliverable is a controlled comparison of 6 prompt strategies, 2 automatic optimisers, schema-constrained
   output and grounded prompt chains, all measured on a held-out labelled set.
2. **Zero-shot vs few-shot?** Zero-shot gives only the instruction and the category list. Few-shot adds labelled
   demonstrations, so the model learns the label boundaries in context (e.g. "Amazon Fresh → Food" vs "Amazon → Shopping").
3. **Why does Python calculate totals?** LLMs are unreliable at arithmetic and can make up figures. Python is exact
   and auditable. The LLM only explains verified numbers, and the grounding checker enforces this.
4. **What is structured output, and why validate the JSON?** The model must return a fixed schema (category,
   confidence, explanation, needs_review). Pydantic rejects missing fields, out-of-range confidence or invalid
   categories, so bad output never reaches the UI. It gets repaired or flagged instead (RQ2).
5. **How is accuracy measured?** Predictions on the 60 untouched test transactions are compared with human labels:
   accuracy plus macro-F1 (so rare categories count equally), plus accuracy on the ambiguous subset.
6. **What does DSPy optimise, and how is that different from editing a prompt by hand?** DSPy treats the prompt's
   instructions and demonstrations as parameters and searches them against a metric on training data. Hand
   editing relies on intuition. Our Arm C does the same search over demo sets, and Arm D uses textual feedback in the style of TextGrad.
7. **How does it avoid unsupported financial suggestions?** It gets only verified facts, is told not to invent
   income or debts, is limited to 3 suggestions, has its savings capped by a Python guard-rail, has every ₹ figure
   checked by the grounding checker, and returns a `missing_information` field instead of guessing.
8. **What are the privacy limits?** Uploaded data is sent to the chosen LLM provider when categorising, so real
   users should use the offline mode or anonymised data. Nothing is stored on disk except a cache of
   synthetic-data responses. No credentials and no account numbers are collected.

**Likely follow-ups:**
*Why batches of 20?* Fewer calls, so lower cost and fewer rate-limit problems. The trade-off is that one malformed
response affects 20 items, which is why per-item lenient parsing and a retry exist.
*Why temperature 0?* Consistent, reproducible labels for evaluation.
*What is the offline simulator?* A deterministic keyword scorer that only uses knowledge written in the prompt
(guide words, examples, rules). It is a fallback for the demo, not a model, and its scores are labelled that way everywhere.
*Limitations:* small synthetic dataset, a single labeller, merchants repeat between dev and test, and a regex
grounding checker that only checks numbers, not every claim.
