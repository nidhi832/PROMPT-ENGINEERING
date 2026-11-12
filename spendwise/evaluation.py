"""Evaluation harness (RQ1-RQ4). Prompts/optimisers see only the dev split; metrics are on the held-out test split."""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support

from . import optimizer
from .categorizer import categorise
from .llm import LLM
from .prompts import PromptTemplate, builtin_strategies
from .schemas import CATEGORIES

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "labelled_transactions.csv"


def load_labelled() -> pd.DataFrame:
    return pd.read_csv(DATA)


def score(prompt: PromptTemplate, rows: pd.DataFrame, llm: LLM) -> dict:
    items = rows[["id", "description"]].to_dict("records")
    t0 = time.perf_counter()
    preds, st = categorise(items, prompt, llm)
    wall = time.perf_counter() - t0
    y, p = rows["category"].tolist(), [x.category for x in preds]
    amb = rows["ambiguous"].astype(bool).tolist()
    pr, rc, f1, sup = precision_recall_fscore_support(y, p, labels=CATEGORIES, zero_division=0)
    flagged = [x.needs_review for x in preds]
    wrong = [a != b for a, b in zip(y, p)]
    return {
        "name": prompt.name, "technique": prompt.technique, "description": prompt.description,
        "n": len(rows),
        "accuracy": round(sum(not w for w in wrong) / len(rows), 4),
        "macro_f1": round(f1_score(y, p, labels=CATEGORIES, average="macro", zero_division=0), 4),
        "ambiguous_accuracy": round(sum(1 for a, w in zip(amb, wrong) if a and not w) / max(sum(amb), 1), 4),
        "json_validity": round(st.strict_valid / st.items, 4),
        "usable_output_rate": round((st.items - st.failed) / st.items, 4),
        "review_flag_rate": round(sum(flagged) / len(rows), 4),
        "errors_caught_by_review": round(sum(1 for f, w in zip(flagged, wrong) if f and w) / max(sum(wrong), 1), 4),
        "calls": st.calls, "input_tokens": st.input_tokens, "output_tokens": st.output_tokens,
        "tokens_per_txn": round((st.input_tokens + st.output_tokens) / len(rows), 1),
        "latency_s": round(st.latency_s if st.latency_s else wall, 3),
        "per_category": {c: {"precision": round(a, 3), "recall": round(b, 3), "f1": round(f, 3), "support": int(s)}
                         for c, a, b, f, s in zip(CATEGORIES, pr, rc, f1, sup)},
        "confusion": confusion_matrix(y, p, labels=CATEGORIES).tolist(),
        "predictions": [{"id": i, "description": d, "true": a, "pred": x.category, "confidence": x.confidence,
                         "needs_review": x.needs_review, "explanation": x.explanation}
                        for i, d, a, x in zip(rows["id"], rows["description"], y, preds)],
    }


def run_evaluation(llm: LLM, log=print, optimise: bool = True) -> dict:
    df = load_labelled()
    dev, test = df[df["split"] == "dev"], df[df["split"] == "test"]
    dev_rows = dev.to_dict("records")
    arms: dict[str, PromptTemplate] = builtin_strategies(dev_rows)
    opt_history = {}
    if optimise:
        log("Optimising prompts on DEV split only...")
        c, opt_history["bootstrap"] = optimizer.bootstrap_fewshot(dev_rows, llm, log=log)
        d, opt_history["textgrad"] = optimizer.textgrad_rules(dev_rows, llm, log=log)
        arms[c.name], arms[d.name] = c, d
    out = {"backend": llm.name, "model": llm.model, "is_real_llm": llm.is_real,
           "timestamp": datetime.now().isoformat(timespec="seconds"),
           "dataset": {"total": len(df), "dev": len(dev), "test": len(test),
                       "test_ambiguous": int(test["ambiguous"].sum())},
           "arms": [], "optimizer_history": opt_history,
           "prompts": {k: v.to_dict() for k, v in arms.items()}}
    for name, p in arms.items():
        log(f"Evaluating {name} on {len(test)} held-out test transactions...")
        out["arms"].append(score(p, test, llm))
    RESULTS.mkdir(exist_ok=True)
    tag = llm.name if not llm.is_real else f"{llm.name}_{llm.model}".replace("/", "-")
    (RESULTS / f"eval_{tag}.json").write_text(json.dumps(out, indent=1))
    pd.DataFrame([{k: v for k, v in a.items() if k not in ("per_category", "confusion", "predictions",
                                                                  "description")} for a in out["arms"]]
                 ).to_csv(RESULTS / f"eval_{tag}.csv", index=False)
    (RESULTS / f"optimized_prompts_{tag}.json").write_text(
        json.dumps({k: v.to_dict() for k, v in arms.items() if k.startswith("optimized")}, indent=1))
    log(f"Saved results/eval_{tag}.json")
    return out


def list_results() -> list[Path]:
    return sorted(RESULTS.glob("eval_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
