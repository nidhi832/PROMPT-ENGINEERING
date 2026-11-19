# 💸 SpendWise — Intelligent Personal Finance Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-16%20Passed-2ED573?style=flat-square&logo=pytest&logoColor=white)](tests/)

> **SpendWise** is an intelligent personal-finance assistant built with **Prompt Engineering**, **Automated Prompt Optimization (DSPy & TextGrad)**, and **Retrieval-Augmented Generation (RAG)**.  
> It pairs an executive **React + Tailwind CSS frontend** (inspired by [RealByte Money Manager](https://www.realbyteapps.com/)) with a high-performance **FastAPI backend** running deterministic Python/pandas calculations for a strict **Zero-Hallucination Guarantee**.

---

## 🚀 Quick Start

### Option A: One-Click Launcher (Windows)
Double-click `RUN_SPENDWISE.bat` in the root folder. It automatically boots both the FastAPI backend and Vite React frontend in separate terminal windows.

### Option B: Manual Startup

#### 1. Start the Python AI Backend (FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the API server on port 8000
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```
- **API Health Check**: `http://localhost:8000/api/health`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

#### 2. Start the React Frontend (Vite)
```bash
cd frontend
npm install
npm run dev -- --port 3000
```
- Open **`http://localhost:3000`** in your browser.

---

## 📋 Core Features

| # | Feature | Capability | Prompt Engineering & AI Architecture |
|---|---|---|---|
| **1** | **Expense Import** | Upload CSV with dates, merchants, and amounts; validates columns and rows. | Auto-detects schema, standardizes Indian merchant descriptions, handles missing fields. |
| **2** | **Smart Categorization** | 8 categories: Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other. | Evaluates zero-shot, role-guided, few-shot, and feedback-optimized prompts with confidence scores and review flags. Inline user overrides. |
| **3** | **Live Spending Analysis** | Dynamic monthly cashflow bars, category breakdown donut, and spending pace area charts. | **Zero Hallucinations**: All arithmetic (totals, averages, MoM change) is computed deterministically by Python/pandas. |
| **4** | **Ask SpendWise** | Conversational natural-language Q&A (*"How much did I spend on food in October?"*). | Intent query routing -> pure Python calculation -> LLM explanation -> Grounding verification check. |
| **5** | **Budget Coach** | Enter target monthly budget or savings goal; receive personalized spending suggestions. | Constrained prompt outputs grounded recommendations with estimated monthly savings capped to category averages. |
| **6** | **Monthly Report** | Statement headline, observations, next steps, category breakdowns. | Pydantic-validated `MonthlyReport` schema with instant Markdown and JSON export. |
| **7** | **RAG Financial Advisor** | Knowledge retrieval over Indian tax rules (80D/80C), 50/30/20 rules, delivery markups, and subscription audits. | TF-IDF semantic vector retrieval over policy chunks combined with verified transaction arithmetic and explicit source citations. |

---

## 🧠 Retrieval-Augmented Generation (RAG) Architecture

SpendWise includes a dedicated **RAG Financial Advisor** module (`spendwise/rag.py`) to deliver verified financial guidance without LLM hallucinations:

```
[ User Financial Inquiry ]
           │
           ▼
[ TF-IDF Semantic Vector Retriever ] ──► Queries Indexed Policy Corpus:
           │                             • Section 80D, 80C & WFH Tax Deductions
           │                             • 50/30/20 Rule & Student Living Benchmarks
           │                             • Swiggy / Zomato Markup Audit (18%-35%)
           │                             • Subscription Audit & Cult.fit Economics
           │                             • Emergency Fund Architecture (3-6 Months)
           ▼
[ Ingestion & Context Augmentation ] ──► Injects Top-K Knowledge Chunks +
           │                             Verified Python Transaction Facts
           ▼
[ LLM Synthesis with Grounding ] ──────► Produces Grounded Answer +
                                         Source Citations + Verification Badge
```

### Knowledge Base Documents
1. **50/30/20 Budgeting Rule & Student Benchmarks**: Allocation guidelines (Needs 50%, Wants 30%, Savings 20%) and room-share strategies.
2. **Indian Income Tax (Section 80D, 80C, 80E)**: Deductions up to ₹25,000 for health insurance & ₹5,000 for preventive checkups; clarifies that gym memberships (e.g. Cult.fit) are personal wellness and *not* deductible under 80D.
3. **Food Delivery Markup Audit**: Food aggregator markups (Swiggy/Zomato 18%–35% over dine-in prices), platform convenience fees, and the 2-day home cooking rule.
4. **Subscription & Recurring Audit Framework**: Checklist for identifying "zombie subscriptions" and gym package cost-per-session economics.
5. **Emergency Fund Architecture**: 3-to-6 month reserve targets, liquid fund storage, and revolving credit card APR warnings (36%–48%).

---

## 🔬 Research & Evaluation Suite (Project Plan Section 8)

Six prompt strategies ("arms") are benchmarked on a held-out test split. Optimisers see only the DEV split; 60 held-out TEST transactions (including 10 deliberately ambiguous merchants) are used once at the end.

| Arm | Technique | Description |
|---|---|---|
| `zero_shot_plain` | Zero-shot, free-text | Baseline prompt without JSON constraints |
| `zero_shot_json` | Zero-shot + JSON | Constrained JSON schema output |
| `role_guided` | Role + category guide + rules + JSON | Best manual prompt |
| `few_shot` | Few-shot with labelled demonstrations | Balanced examples selected from DEV split |
| `optimized_bootstrap` | Bootstrap demonstrations | DSPy-inspired few-shot demonstration selection |
| `optimized_textgrad` | Feedback-refined rules | TextGrad-inspired feedback loop deriving negative rules |

### Evaluation Results (`openai/gpt-oss-20b` via Groq, 60 test transactions)

| Arm | Accuracy | Macro F1 | Ambiguous (10) | Strict JSON | Tokens / txn |
|---|---|---|---|---|---|
| `zero_shot_plain` | 93.3% | 0.931 | 80% | n/a | 73.5 |
| `zero_shot_json` | 93.3% | 0.931 | 80% | 33.3% | 168.4 |
| `role_guided` | **100%** | **1.000** | **100%** | **100%** | 112.4 |
| `few_shot` | **100%** | **1.000** | **100%** | **100%** | 104.6 |
| `optimized_bootstrap` | **100%** | **1.000** | **100%** | 66.7% | 140.2 |
| `optimized_textgrad` | **100%** | **1.000** | **100%** | **100%** | 113.7 |

Full report: `results/eval_openai-compatible_openai-gpt-oss-20b.json`.

---

## 📂 Project Architecture

```
PROMPT-ENGINEERING/
├── api.py                    # FastAPI server exposing endpoints for frontend & RAG
├── RUN_SPENDWISE.bat         # Single-click launcher for Windows (Backend + Frontend)
├── RUN_SPENDWISE.command     # Single-click launcher for macOS / Linux
├── spendwise/                # Core Python AI prompt engineering & RAG engine
│   ├── analytics.py          # Deterministic pandas financial calculations (Zero Hallucination)
│   ├── assistant.py          # Q&A query router, budget coach & monthly reports
│   ├── categorizer.py        # LLM transaction batching & Pydantic validation
│   ├── data.py               # CSV import normalization & validation
│   ├── evaluation.py         # Benchmark runner for prompt strategy arms
│   ├── llm.py                # Multi-backend wrapper (Gemini, Claude, Groq, Offline Simulator)
│   ├── optimizer.py          # Prompt optimizers (DSPy bootstrap & TextGrad feedback)
│   ├── prompts.py            # Versioned prompt template library
│   ├── rag.py                # RAG module: TF-IDF vector index, semantic retrieval & synthesis
│   └── schemas.py            # Pydantic data models & schemas
├── data/
│   ├── sample_expenses.csv   # 168 real student transactions (Aug–Oct 2026)
│   └── labelled_transactions.csv # Ground-truth labelled dataset (Dev/Test split)
├── frontend/                 # React 18 + TypeScript + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/       # InteractiveDashboard, Hero, Features, HelpCenter
│   │   └── data/             # Interfaces & baseline mock datasets
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── tests/
│   ├── test_core.py          # Core feature unit tests (13 tests)
│   └── test_rag.py           # RAG retrieval & grounding unit tests (3 tests)
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check and service status |
| `GET` | `/api/data/sample` | Returns 168 student transactions with KPIs and category breakdowns |
| `POST` | `/api/data/upload` | Uploads and parses user CSV via pandas |
| `POST` | `/api/categorize` | Runs batch AI categorization using the selected prompt strategy |
| `POST` | `/api/assistant/ask` | Natural language Q&A with grounded arithmetic verification |
| `POST` | `/api/assistant/budget` | Generates budget coach suggestions with saving estimates |
| `POST` | `/api/assistant/report` | Generates structured monthly financial report |
| `GET` | `/api/rag/knowledge-base`| Returns all indexed personal finance policy documents |
| `POST` | `/api/rag/ask` | Executes RAG semantic retrieval + grounded LLM advice with citations |
| `GET` | `/api/evaluation/results`| Returns latest research evaluation benchmark results |

---

## 🧪 Running Tests

Run the complete test suite anytime with:

```bash
python -m pytest -v tests
```

To test all 6 core functional features via script:
```bash
python test_project_plan_features.py
```

---

## 🔒 Safety, Privacy & Boundaries

- **Educational Only**: Does not connect to real bank accounts or request banking credentials.
- **Session-Only Processing**: No financial data is retained after the session closes.
- **Zero Hallucination Guarantee**: All arithmetic calculations are executed in Python and verified via grounding checks before display.
