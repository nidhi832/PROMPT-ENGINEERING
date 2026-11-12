"""All arithmetic lives here (pandas). The LLM only ever *explains* numbers produced by this module."""
from __future__ import annotations

import pandas as pd

from .schemas import CATEGORIES

DISCRETIONARY = ["Food", "Shopping", "Entertainment", "Transport", "Other"]


def month_label(m: str) -> str:
    return pd.Period(m, freq="M").strftime("%B %Y")


def by_category(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("category")["amount"].agg(total="sum", count="size", average="mean").reset_index()
    g["share_pct"] = 100 * g["total"] / g["total"].sum()
    return g.sort_values("total", ascending=False).round(2).reset_index(drop=True)


def by_month(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("month")["amount"].agg(total="sum", count="size").reset_index().round(2)


def month_category(df: pd.DataFrame) -> pd.DataFrame:
    p = df.pivot_table(index="month", columns="category", values="amount", aggfunc="sum", fill_value=0)
    return p.reindex(columns=[c for c in CATEGORIES if c in p.columns]).round(2)


def top_merchants(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    return (df.groupby("merchant")["amount"].agg(total="sum", visits="size").reset_index()
            .sort_values("total", ascending=False).head(n).round(2))


def kpis(df: pd.DataFrame) -> dict:
    months = df["month"].nunique()
    bm = by_month(df)
    last, prev = (bm.iloc[-1], bm.iloc[-2]) if len(bm) >= 2 else (bm.iloc[-1], None)
    return {
        "total": round(df["amount"].sum(), 2),
        "transactions": int(len(df)),
        "months": int(months),
        "monthly_average": round(df["amount"].sum() / max(months, 1), 2),
        "latest_month": last["month"],
        "latest_month_total": round(float(last["total"]), 2),
        "mom_change_pct": None if prev is None else round(100 * (last["total"] - prev["total"]) / prev["total"], 1),
        "largest": df.loc[df["amount"].idxmax(), ["date", "description", "amount"]].to_dict(),
    }


def month_facts(df: pd.DataFrame, month: str) -> dict:
    """Verified facts for one month - this dict is exactly what the report/budget prompts receive."""
    m = df[df["month"] == month]
    months = sorted(df["month"].unique())
    idx = months.index(month)
    prev = df[df["month"] == months[idx - 1]] if idx > 0 else None
    cats = by_category(m)
    facts = {
        "month": month,
        "month_name": month_label(month),
        "total_spent": round(m["amount"].sum(), 2),
        "transaction_count": int(len(m)),
        "category_totals": {r.category: round(r.total, 2) for r in cats.itertuples()},
        "category_share_pct": {r.category: round(r.share_pct, 1) for r in cats.itertuples()},
        "largest_transaction": {"description": m.loc[m["amount"].idxmax(), "description"],
                                "amount": round(float(m["amount"].max()), 2)},
        "top_merchants": {r.merchant: round(r.total, 2) for r in top_merchants(m, 5).itertuples()},
    }
    if prev is not None:
        pt = prev.groupby("category")["amount"].sum()
        facts["previous_month"] = months[idx - 1]
        facts["previous_month_name"] = month_label(months[idx - 1])
        facts["previous_total"] = round(prev["amount"].sum(), 2)
        facts["change_vs_previous_pct"] = round(100 * (facts["total_spent"] - facts["previous_total"])
                                                / facts["previous_total"], 1)
        facts["category_change_vs_previous"] = {
            c: round(facts["category_totals"].get(c, 0) - float(pt.get(c, 0)), 2)
            for c in sorted(set(pt.index) | set(facts["category_totals"]))}
    return facts


def budget_facts(df: pd.DataFrame, monthly_budget: float | None, savings_goal: float | None,
                 income: float | None) -> dict:
    months = sorted(df["month"].unique())
    latest = df[df["month"] == months[-1]]
    avg_cat = (df.groupby(["month", "category"])["amount"].sum().groupby("category").mean())
    facts = {
        "months_of_data": len(months),
        "latest_month": months[-1],
        "latest_month_total": round(latest["amount"].sum(), 2),
        "average_monthly_total": round(df.groupby("month")["amount"].sum().mean(), 2),
        "average_monthly_by_category": {k: round(v, 2) for k, v in avg_cat.sort_values(ascending=False).items()},
        "user_monthly_budget": monthly_budget,
        "user_monthly_savings_goal": savings_goal,
        "user_monthly_income": income,
    }
    if monthly_budget:
        facts["gap_vs_budget"] = round(facts["average_monthly_total"] - monthly_budget, 2)
    if income and savings_goal:
        facts["spending_allowed_for_goal"] = round(income - savings_goal, 2)
        facts["gap_vs_goal"] = round(facts["average_monthly_total"] - facts["spending_allowed_for_goal"], 2)
    return facts
