# 💸 SpendWise — Intelligent Personal Finance Assistant

**An intelligent personal-finance assistant built with Prompt Engineering and Automated Prompt Optimization.**  
Features an interactive **React + Tailwind CSS frontend** inspired by [RealByte Money Manager](https://www.realbyteapps.com/) and a high-performance **FastAPI backend**.

---

## 🚀 Quick Start (Run Both Components)

### 1. Start the Python AI Backend (FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the API server on port 8000
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```
- API Health Check: `http://localhost:8000/api/health`
- Interactive API Docs: `http://localhost:8000/docs`

### 2. Start the React Frontend
```bash
cd frontend
npm install
npm run dev -- --port 3000
```
- Open `http://localhost:3000` in your web browser.

---

## 📋 Core Features (Project Plan Section 5)

| # | Feature | Capability | Prompt Engineering & AI Role |
|---|---|---|---|
| **1** | **Expense Import** | Upload CSV containing date, description, amount; row validation. | Auto-detects columns, normalizes descriptions, handles missing fields. |
| **2** | **Smart Categorization** | Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other. | Zero-shot & few-shot prompts with confidence score and `needs_review` flags. User can edit/override inline. |
| **3** | **Spending Analysis** | Interactive donut chart, monthly cashflow bars, spending velocity area chart. | Arithmetic computed deterministically by Python (pandas), zero hallucinations. |
| **4** | **Ask SpendWise** | Conversational natural-language Q&A (*"How much did I spend on food in October?"*). | Intent query routing, pandas computation, grounded explanation, and grounding verification badge. |
| **5** | **Budget Suggestions** | Enter monthly budget or savings goal; receive practical suggestions. | Constrained prompt produces grounded suggestions with estimated monthly savings and guard-rails. |
| **6** | **Monthly Report** | Statement headline, observations, next steps, category breakdowns. | Pydantic validated `MonthlyReport` schema with one-click Markdown and JSON downloads. |

---

## 🔬 Research & Evaluation Suite (Project Plan Section 8)

Six prompt strategies ("arms") are compared on a held-out test split. Optimisers see only the DEV split;
the 60 TEST transactions (10 deliberately ambiguous merchants) are used once, at the end.

| Arm | Technique |
|---|---|
| `zero_shot_plain` | Zero-shot, free-text answer (baseline) |
| `zero_shot_json` | Zero-shot + JSON schema |
| `role_guided` | Role + category guide + rules + JSON (best manual prompt) |
| `few_shot` | Few-shot with labelled demonstrations |
| `optimized_bootstrap` | Auto-selected demonstrations (re-implementation of the DSPy BootstrapFewShot idea) |
| `optimized_textgrad` | Feedback-refined rules (re-implementation of the TextGrad idea) |

### Results: `openai/gpt-oss-20b` via Groq, single run, 60 test transactions

| Arm | Accuracy | Macro F1 | Ambiguous (10) | Strict JSON | Tokens / txn |
|---|---|---|---|---|---|
| zero_shot_plain | 93.3% | 0.931 | 80% | n/a | 73.5 |
| zero_shot_json | 93.3% | 0.931 | 80% | 33.3% | 168.4 |
| role_guided | 100% | 1.000 | 100% | 100% | 112.4 |
| few_shot | 100% | 1.000 | 100% | 100% | 104.6 |
| optimized_bootstrap | 100% | 1.000 | 100% | 66.7% | 140.2 |
| optimized_textgrad | 100% | 1.000 | 100% | 100% | 113.7 |

Full output: `results/eval_openai-compatible_openai-gpt-oss-20b.json`.

**Findings**
- Structured prompting fixed all 4 zero-shot errors (93.3% -> 100%), but with only 4 differing
  transactions the gap is not statistically significant (exact McNemar p = 0.125).
- Clearest effect: a JSON schema alone gave 33% strict JSON validity; adding role, category guide and
  rules gave 100%.
- The optimisers gave no extra gain because the best manual prompt already scored 100% (ceiling effect).

**Limitations**
- Synthetic transactions; 60 test rows; one run with one model.
- 40 of the 60 test merchants also appear in the DEV split, which can favour the few-shot and optimised arms.
- The "DSPy" and "TextGrad" arms re-implement those ideas; they do not use the libraries.

**Reproduce** (free Groq key in `OPENAI_API_KEY`; the model is pinned for the whole run):
```bash
python evaluate.py --backend openai-compatible --list-models
python evaluate.py --backend openai-compatible --model openai/gpt-oss-20b
```
`python evaluate.py --backend offline-simulator` runs without a key, but its scores come from a
keyword simulator, not a language model.

Run tests anytime with:
```bash
python -m pytest -v tests
```

---

## 📂 Project Architecture

```
PROMPT-ENGINEERING/
├── api.py                    # FastAPI server exposing endpoints for frontend
├── spendwise/                # Core Python prompt engineering engine
│   ├── analytics.py          # Deterministic pandas financial calculations
│   ├── assistant.py          # Q&A query router, budget coach & monthly reports
│   ├── categorizer.py        # LLM transaction batching & Pydantic validation
│   ├── data.py               # CSV import normalization & validation
│   ├── evaluation.py         # Held-out test set benchmark runner (Arms A-F)
│   ├── llm.py                # Multi-backend wrapper (Gemini, Claude, Groq, Offline)
│   ├── optimizer.py          # DSPy & TextGrad prompt optimizers
│   ├── prompts.py            # Built-in prompt template strategies
│   └── schemas.py            # Pydantic schemas (PredictedCategory, MonthlyReport)
├── data/
│   ├── sample_expenses.csv   # 168 real student transactions (Aug–Oct 2026)
│   └── labelled_transactions.csv # Ground-truth labelled dataset (Dev/Test split)
├── frontend/                 # React + TypeScript + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/       # Hero, Features, Dashboard Workspace, Help Center
│   │   └── data/             # Mock datasets & interfaces
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── tests/
│   └── test_core.py          # Comprehensive test suite
├── requirements.txt          # Python dependencies (FastAPI, uvicorn, pandas, pydantic)
└── README.md
```

---

## 🔒 Safety, Privacy & Boundaries
- **Educational Only**: Does not connect to real bank accounts or request banking credentials.
- **Session-Only Processing**: No financial data is retained after sessions.
- **Zero Hallucination Guarantee**: All arithmetic is executed in Python and verified via grounding checks before display.
