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

The project evaluates prompt engineering techniques on a held-out test split (70/30) without data leakage:
- **Arm A**: Zero-shot Plain Text (Baseline)
- **Arm B**: Zero-shot with JSON Schema
- **Arm C**: Few-shot with Labelled Demonstrations
- **Arm D**: Role-based Prompting (Budget Coach persona)
- **Arm E**: DSPy Prompt Optimization (`BootstrapFewShot`)
- **Arm F**: TextGrad Refinement (Iterative textual gradients)

### Metrics Reported:
- **Category Accuracy** (`93.3%` on optimized prompt vs `68.3%` on zero-shot)
- **Macro F1 Score** (`0.935` balancing rare categories)
- **Ambiguous Merchant Accuracy** (`90.0%` vs `30.0%`)
- **Strict JSON Validity** (`100%`)

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
