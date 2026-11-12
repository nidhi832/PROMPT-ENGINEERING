"""Prompt chain for Ask SpendWise, budget suggestions and the monthly report (Features 4-6).

Chain:  question -> [LLM: route to structured intent] -> [Python: compute] -> [LLM: explain verified result]
        -> [Python: grounding check - every ₹ amount in the answer must exist in the verified result]
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import pandas as pd
from pydantic import ValidationError

from . import analytics, prompts
from .llm import LLM
from .schemas import BudgetAdvice, MonthlyReport, QueryIntent

# ---------------------------------------------------------------- grounding check (RQ4)

NUM_RE = re.compile(r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)|([\d,]+(?:\.\d+)?)\s*%", re.I)


def _collect_numbers(obj, acc: set):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        acc.add(round(float(obj), 2)); acc.add(round(float(obj))); acc.add(round(abs(float(obj)), 2))
        acc.add(round(abs(float(obj)), 1))
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_numbers(v, acc)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect_numbers(v, acc)


@dataclass
class Grounding:
    amounts_checked: int = 0
    unsupported: list[str] = field(default_factory=list)

    @property
    def grounded(self) -> bool:
        return not self.unsupported


def grounding_check(text: str, facts) -> Grounding:
    """Every ₹ amount / percentage quoted in `text` must appear in `facts` (allowing rounding)."""
    known: set = set()
    _collect_numbers(facts, known)
    g = Grounding()
    for m in NUM_RE.finditer(text):
        raw = m.group(1) or m.group(2)
        try:
            v = float(raw.replace(",", ""))
        except ValueError:
            continue
        g.amounts_checked += 1
        if not any(abs(v - k) <= max(0.51, 0.005 * abs(k)) for k in known):
            g.unsupported.append(m.group(0))
    return g


def _json(text: str):
    return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip()))


# ---------------------------------------------------------------- Ask SpendWise

def execute_intent(df: pd.DataFrame, q: QueryIntent) -> dict:
    """Pure-Python calculation of the routed intent. This is the only place answers are computed."""
    d = df
    scope = []
    if q.category:
        d = d[d["category"] == q.category]; scope.append(q.category)
    if q.month and q.intent != "compare_months":
        d = d[d["month"] == q.month]; scope.append(analytics.month_label(q.month))
    res = {"intent": q.intent, "scope": " in ".join(scope) if scope else "all your data",
           "matching_transactions": int(len(d))}
    if q.intent == "unsupported":
        return res
    if q.intent == "compare_months":
        months = sorted(df["month"].unique())
        a = q.month or months[-1]
        b = q.month_b or (months[months.index(a) - 1] if months.index(a) > 0 else months[-1])
        ta, tb = (round(float(d[d["month"] == m]["amount"].sum()), 2) for m in (a, b))
        res.update({"month": analytics.month_label(a), "month_b": analytics.month_label(b),
                    "scope_category": q.category or "all categories", "total_month": ta, "total_month_b": tb,
                    "difference": round(ta - tb, 2),
                    "difference_pct": round(100 * (ta - tb) / tb, 1) if tb else 0.0,
                    "matching_transactions": int(len(d[d["month"].isin([a, b])]))})
        return res
    res["total"] = round(float(d["amount"].sum()), 2)
    if q.intent == "average" and len(d):
        res["average"] = round(float(d["amount"].mean()), 2)
    if q.intent in ("by_category", "top_categories"):
        s = d.groupby("category")["amount"].sum().sort_values(ascending=False).round(2)
        res["categories"] = s.head(q.n if q.intent == "top_categories" else 20).to_dict()
    if q.intent in ("largest", "list"):
        dd = d.sort_values("amount", ascending=False) if q.intent == "largest" else d.sort_values("date")
        res["transactions"] = [{"date": r.date.strftime("%d %b %Y"), "description": r.description,
                                "amount": round(r.amount, 2), "category": r.category}
                               for r in dd.head(q.n if q.intent == "largest" else 15).itertuples()]
    return res


@dataclass
class Answer:
    question: str
    intent: QueryIntent | None
    result: dict
    text: str
    grounding: Grounding
    trace: list[dict]          # every prompt + response in the chain, for the "show your work" panel


def ask(df: pd.DataFrame, question: str, llm: LLM) -> Answer:
    trace = []
    months = sorted(df["month"].unique())
    cats = sorted(df["category"].unique())
    s, u = prompts.query_router(question, months, cats)
    r = llm.complete(s, u, json_mode=True)
    trace.append({"step": "1. Route question -> structured intent (LLM)", "prompt": u, "response": r.text,
                  "tokens": r.input_tokens + r.output_tokens})
    try:
        intent = QueryIntent.model_validate(_json(r.text))
    except (json.JSONDecodeError, ValidationError) as e:
        trace.append({"step": "Intent failed validation", "prompt": "", "response": str(e)[:400], "tokens": 0})
        intent = QueryIntent(intent="unsupported")
    result = execute_intent(df, intent)
    trace.append({"step": "2. Compute answer with pandas (Python)", "prompt": intent.model_dump_json(),
                  "response": json.dumps(result, default=str, indent=1), "tokens": 0})
    s, u = prompts.grounded_answer(question, result)
    r = llm.complete(s, u, json_mode=False)
    text = r.text.strip()
    g = grounding_check(text, result)
    trace.append({"step": "3. Explain verified result (LLM)", "prompt": u, "response": text,
                  "tokens": r.input_tokens + r.output_tokens})
    trace.append({"step": "4. Grounding check (Python)", "prompt": "",
                  "response": f"{g.amounts_checked} amounts checked, unsupported: {g.unsupported or 'none'}",
                  "tokens": 0})
    return Answer(question, intent, result, text, g, trace)


# ---------------------------------------------------------------- budget suggestions + monthly report

def _structured(llm: LLM, system: str, user: str, model):
    """Call -> validate with Pydantic -> one retry with the validation error fed back."""
    r = llm.complete(system, user, json_mode=True)
    attempts = [r.text]
    try:
        return model.model_validate(_json(r.text)), attempts
    except (json.JSONDecodeError, ValidationError) as e:
        r2 = llm.complete(system, user + f"\n\nYour previous output failed validation: {str(e)[:300]}. "
                                          "Return ONLY corrected JSON.", json_mode=True)
        attempts.append(r2.text)
        return model.model_validate(_json(r2.text)), attempts


def budget_advice(df: pd.DataFrame, llm: LLM, monthly_budget=None, savings_goal=None, income=None):
    facts = analytics.budget_facts(df, monthly_budget, savings_goal, income)
    s, u = prompts.budget_suggestions(facts)
    advice, attempts = _structured(llm, s, u, BudgetAdvice)
    # Python guard-rail: a suggestion's saving can't exceed what is actually spent in that category
    avg = facts["average_monthly_by_category"]
    flags = []
    for sg in advice.suggestions:
        if sg.category and sg.estimated_monthly_saving and sg.estimated_monthly_saving > avg.get(sg.category, 0):
            flags.append(f"'{sg.title}': saving ₹{sg.estimated_monthly_saving:,.0f} exceeds category spend - capped")
            sg.estimated_monthly_saving = avg.get(sg.category, 0)
    text = advice.summary + " " + " ".join(f"{x.title} {x.detail}" for x in advice.suggestions)
    allowed = {**facts, "savings": [x.estimated_monthly_saving for x in advice.suggestions]}
    g = grounding_check(text, allowed)
    return advice, facts, g, flags, {"prompt": u, "responses": attempts}


def monthly_report(df: pd.DataFrame, month: str, llm: LLM):
    facts = analytics.month_facts(df, month)
    s, u = prompts.monthly_report(facts)
    report, attempts = _structured(llm, s, u, MonthlyReport)
    g = grounding_check(" ".join([report.headline, *report.observations, *report.next_steps]), facts)
    return report, facts, g, {"prompt": u, "responses": attempts}
