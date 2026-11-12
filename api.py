"""SpendWise FastAPI Backend Server.
Exposes the core SpendWise prompt engineering engine, analytics, categorizer,
assistant Q&A, budget coach, monthly reports, and evaluation suite to the React frontend.
Run: uvicorn api:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from spendwise import analytics, assistant
from spendwise.categorizer import categorise
from spendwise.data import load_transactions
from spendwise.evaluation import list_results, load_labelled, run_evaluation
from spendwise.llm import make_llm
from spendwise.prompts import builtin_strategies
from spendwise.schemas import CATEGORIES

ROOT = Path(__file__).parent
SAMPLE_CSV_PATH = ROOT / "data" / "sample_expenses.csv"

app = FastAPI(title="SpendWise AI API", version="2.0.0")

# Enable CORS for React frontend (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session state for loaded transactions
SESSION_DATA: Dict[str, Any] = {
    "df": None,
    "import_rep": None,
    "overrides": {},
    "chat": [],
}


def get_default_df():
    if SESSION_DATA["df"] is None or SESSION_DATA["df"].empty:
        raw = SAMPLE_CSV_PATH.read_bytes()
        df, rep = load_transactions(io.BytesIO(raw))
        # Default categorization with few_shot offline simulator
        llm = make_llm("offline-simulator")
        labelled = load_labelled()
        strat = builtin_strategies(labelled[labelled["split"] == "dev"].to_dict("records"))["few_shot"]
        preds, _ = categorise(df[["id", "description"]].to_dict("records"), strat, llm)
        df["category"] = [p.category for p in preds]
        df["confidence"] = [p.confidence for p in preds]
        df["needs_review"] = [p.needs_review for p in preds]
        df["explanation"] = [p.explanation for p in preds]
        SESSION_DATA["df"] = df
        SESSION_DATA["import_rep"] = rep
    return SESSION_DATA["df"]


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SpendWise AI Backend"}


@app.get("/api/data/sample")
def get_sample_transactions():
    df = get_default_df().copy()
    k = analytics.kpis(df)
    cats = analytics.by_category(df)
    records = df.to_dict("records")
    for r in records:
        if "date" in r and hasattr(r["date"], "isoformat"):
            r["date"] = r["date"].strftime("%Y-%m-%d")
    return {
        "transactions": records,
        "kpis": k,
        "by_category": cats.to_dict("records"),
        "total_count": len(df),
    }


@app.post("/api/data/upload")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df, rep = load_transactions(io.BytesIO(content))
        if df.empty:
            raise HTTPException(status_code=400, detail="No valid transaction rows found in CSV.")
        
        # Categorize
        llm = make_llm("offline-simulator")
        labelled = load_labelled()
        strat = builtin_strategies(labelled[labelled["split"] == "dev"].to_dict("records"))["few_shot"]
        preds, cstats = categorise(df[["id", "description"]].to_dict("records"), strat, llm)
        df["category"] = [p.category for p in preds]
        df["confidence"] = [p.confidence for p in preds]
        df["needs_review"] = [p.needs_review for p in preds]
        df["explanation"] = [p.explanation for p in preds]
        
        SESSION_DATA["df"] = df
        SESSION_DATA["import_rep"] = rep
        
        records = df.to_dict("records")
        for r in records:
            if "date" in r and hasattr(r["date"], "isoformat"):
                r["date"] = r["date"].strftime("%Y-%m-%d")

        return {
            "success": True,
            "filename": file.filename,
            "rows_in": rep.rows_in,
            "rows_ok": rep.rows_ok,
            "notes": rep.notes,
            "issues": rep.issues,
            "transactions": records,
            "kpis": analytics.kpis(df),
            "by_category": analytics.by_category(df).to_dict("records"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class CategorizeRequest(BaseModel):
    strategy: str = "few_shot"
    backend: str = "offline-simulator"
    model: Optional[str] = None
    api_key: Optional[str] = None


@app.post("/api/categorize")
def run_categorization(req: CategorizeRequest):
    df = get_default_df().copy()
    kw = {"api_key": req.api_key} if req.api_key else {}
    llm = make_llm(req.backend, req.model or None, **kw)
    
    labelled = load_labelled()
    strategies = builtin_strategies(labelled[labelled["split"] == "dev"].to_dict("records"))
    if req.strategy not in strategies:
        strat = strategies["few_shot"]
    else:
        strat = strategies[req.strategy]

    preds, cstats = categorise(df[["id", "description"]].to_dict("records"), strat, llm)
    df["category"] = [p.category for p in preds]
    df["confidence"] = [p.confidence for p in preds]
    df["needs_review"] = [p.needs_review for p in preds]
    df["explanation"] = [p.explanation for p in preds]
    SESSION_DATA["df"] = df

    records = df.to_dict("records")
    for r in records:
        if "date" in r and hasattr(r["date"], "isoformat"):
            r["date"] = r["date"].strftime("%Y-%m-%d")

    return {
        "transactions": records,
        "stats": {
            "calls": cstats.calls,
            "tokens": cstats.input_tokens + cstats.output_tokens,
            "strict_valid_pct": round(100 * cstats.strict_valid / max(cstats.items, 1), 1),
            "flagged_count": int(df["needs_review"].sum()),
        },
        "kpis": analytics.kpis(df),
        "by_category": analytics.by_category(df).to_dict("records"),
    }


class OverrideRequest(BaseModel):
    transaction_id: str
    new_category: str


@app.post("/api/override")
def override_category(req: OverrideRequest):
    df = get_default_df()
    if req.new_category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    mask = df["id"] == req.transaction_id
    if not mask.any():
        raise HTTPException(status_code=404, detail="Transaction not found")
    df.loc[mask, "category"] = req.new_category
    df.loc[mask, "needs_review"] = False
    SESSION_DATA["overrides"][req.transaction_id] = req.new_category
    return {"success": True, "kpis": analytics.kpis(df), "by_category": analytics.by_category(df).to_dict("records")}


class AskRequest(BaseModel):
    question: str
    backend: str = "offline-simulator"
    model: Optional[str] = None
    api_key: Optional[str] = None


@app.post("/api/assistant/ask")
def ask_question(req: AskRequest):
    df = get_default_df()
    kw = {"api_key": req.api_key} if req.api_key else {}
    llm = make_llm(req.backend, req.model or None, **kw)
    try:
        ans = assistant.ask(df, req.question, llm)
        return {
            "answer": ans.text,
            "intent": ans.intent.intent if ans.intent else "unknown",
            "grounded": ans.grounding.grounded,
            "figures_verified": ans.grounding.amounts_checked,
            "unsupported": ans.grounding.unsupported,
            "trace": ans.trace,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class BudgetRequest(BaseModel):
    monthly_budget: Optional[float] = None
    savings_goal: Optional[float] = None
    income: Optional[float] = None
    backend: str = "offline-simulator"
    model: Optional[str] = None
    api_key: Optional[str] = None


@app.post("/api/assistant/budget")
def get_budget_advice(req: BudgetRequest):
    df = get_default_df()
    kw = {"api_key": req.api_key} if req.api_key else {}
    llm = make_llm(req.backend, req.model or None, **kw)
    try:
        advice, facts, g, flags, trace = assistant.budget_advice(
            df, llm, monthly_budget=req.monthly_budget, savings_goal=req.savings_goal, income=req.income
        )
        return {
            "summary": advice.summary,
            "suggestions": [s.model_dump() for s in advice.suggestions],
            "missing_information": advice.missing_information,
            "facts": facts,
            "grounded": g.grounded,
            "flags": flags,
            "trace": trace,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ReportRequest(BaseModel):
    month: str = "2026-10"
    backend: str = "offline-simulator"
    model: Optional[str] = None
    api_key: Optional[str] = None


@app.post("/api/assistant/report")
def get_monthly_report(req: ReportRequest):
    df = get_default_df()
    kw = {"api_key": req.api_key} if req.api_key else {}
    llm = make_llm(req.backend, req.model or None, **kw)
    try:
        rep, facts, g, trace = assistant.monthly_report(df, req.month, llm)
        return {
            "headline": rep.headline,
            "observations": rep.observations,
            "next_steps": rep.next_steps,
            "facts": facts,
            "grounded": g.grounded,
            "trace": trace,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluation/results")
def get_evaluation_results():
    files = list_results()
    if not files:
        return {"results": None}
    res = json.loads(files[0].read_text())
    return {"results": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
