"""CSV import + validation with explicit rules (Feature 1). No LLM involved here."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

COLUMN_ALIASES = {
    "date": ["date", "txn date", "transaction date", "value date", "posting date"],
    "description": ["description", "narration", "details", "merchant", "particulars", "remarks", "note"],
    "amount": ["amount", "debit", "withdrawal", "withdrawal amt", "spent", "value", "amount (inr)"],
    "category": ["category", "label"],
}


@dataclass
class ImportReport:
    rows_in: int = 0
    rows_ok: int = 0
    issues: list[dict] = field(default_factory=list)   # {"row": n, "problem": "..."}
    notes: list[str] = field(default_factory=list)


def _map_columns(df: pd.DataFrame) -> dict[str, str]:
    lower = {c.strip().lower(): c for c in df.columns}
    mapping = {}
    for target, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if a in lower:
                mapping[lower[a]] = target
                break
    return mapping


def _parse_amount(x) -> float | None:
    if pd.isna(x):
        return None
    s = re.sub(r"[₹$,\s]|INR|Rs\.?", "", str(x), flags=re.I)
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return None


def clean_description(s: str) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s


def merchant_key(desc: str) -> str:
    """Normalise a description to a merchant-like key for grouping (UPI/123456/Swiggy order #12 -> swiggy order)."""
    s = desc.lower()
    s = re.sub(r"^upi/\d+/", "", s)
    s = re.sub(r"#?\d+", "", s)
    s = re.sub(r"[^a-z&.\s-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" -")
    return s.title() or "Unknown"


def load_transactions(source) -> tuple[pd.DataFrame, ImportReport]:
    """Read a CSV (path or file-like) and return a clean frame: id, date, description, amount, month, merchant."""
    raw = pd.read_csv(source)
    rep = ImportReport(rows_in=len(raw))
    mapping = _map_columns(raw)
    missing = {"date", "description", "amount"} - set(mapping.values())
    if missing:
        raise ValueError(f"CSV is missing required column(s): {', '.join(sorted(missing))}. "
                         f"Found: {', '.join(raw.columns)}")
    df = raw.rename(columns=mapping)[[c for c in ["date", "description", "amount", "category"]
                                      if c in mapping.values()]].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed", dayfirst=False)
    df["amount"] = df["amount"].map(_parse_amount)
    df["description"] = df["description"].fillna("").map(clean_description)

    keep = []
    for i, r in df.iterrows():
        row_no = i + 2  # header is row 1
        if pd.isna(r["date"]):
            rep.issues.append({"row": row_no, "problem": "unreadable or missing date"}); continue
        if r["amount"] is None or pd.isna(r["amount"]):
            rep.issues.append({"row": row_no, "problem": "missing or non-numeric amount"}); continue
        if r["amount"] == 0:
            rep.issues.append({"row": row_no, "problem": "zero amount"}); continue
        if not r["description"]:
            rep.issues.append({"row": row_no, "problem": "empty description"}); continue
        keep.append(i)
    df = df.loc[keep].copy()

    if (df["amount"] < 0).mean() > 0.5:
        rep.notes.append("Most amounts were negative (bank-export style); treated them as spending.")
    if (df["amount"] < 0).any():
        df["amount"] = df["amount"].abs()

    dups = df.duplicated(subset=["date", "description", "amount"]).sum()
    if dups:
        rep.notes.append(f"{dups} exact duplicate row(s) found and kept - check they are genuine.")

    df = df.sort_values("date").reset_index(drop=True)
    df.insert(0, "id", [f"T{i + 1:03d}" for i in range(len(df))])
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["merchant"] = df["description"].map(merchant_key)
    df["amount"] = df["amount"].round(2)
    rep.rows_ok = len(df)
    return df, rep
