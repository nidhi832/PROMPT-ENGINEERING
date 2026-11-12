"""Automated prompt optimisation, using the DEV split only (test stays untouched).

Arm C  bootstrap_fewshot  - DSPy BootstrapFewShotWithRandomSearch idea, implemented from scratch:
                            run the base prompt on dev-train, collect the hard (misclassified) examples,
                            build several candidate demo sets (balanced + hard), keep the set with the best
                            dev-validation accuracy.
Arm D  textgrad_rules     - TextGrad idea: the LLM reads its own validation mistakes and writes natural-language
                            "gradients" (correction rules) that are appended to the prompt; keep an update only
                            if dev-validation accuracy does not drop.

Both are deliberately small so they run on free-tier API limits. Real DSPy/TextGrad can be swapped in later.
"""
from __future__ import annotations

import json
import random
import re

from pydantic import BaseModel

from .categorizer import categorise
from .llm import LLM
from .prompts import PromptTemplate, pick_balanced_examples, role_guided, textgrad_feedback


def _split_dev(dev: list[dict], seed=0):
    rng = random.Random(seed)
    d = dev[:]
    rng.shuffle(d)
    cut = int(len(d) * 0.65)
    return d[:cut], d[cut:]


def accuracy(prompt: PromptTemplate, rows: list[dict], llm: LLM):
    preds, stats = categorise([{"id": r["id"], "description": r["description"]} for r in rows], prompt, llm)
    errs = [{**r, "predicted": p.category} for r, p in zip(rows, preds) if p.category != r["category"]]
    return 1 - len(errs) / len(rows), errs, stats


def bootstrap_fewshot(dev: list[dict], llm: LLM, n_candidates: int = 4, max_hard: int = 8, log=print):
    train, val = _split_dev(dev)
    base = role_guided()
    base_acc, errs, _ = accuracy(base, train, llm)
    log(f"[C] base prompt dev-train acc={base_acc:.3f}, {len(errs)} hard examples")
    history = []
    best, best_acc = None, -1.0
    for k in range(n_candidates):
        rng = random.Random(100 + k)
        demos = pick_balanced_examples(train, per_category=1, seed=100 + k)
        hard = rng.sample(errs, min(max_hard, len(errs)))
        demos += [(e["description"], e["category"]) for e in hard if (e["description"], e["category"]) not in demos]
        cand = PromptTemplate(**{**base.to_dict(), "examples": demos})
        acc, _, _ = accuracy(cand, val, llm)
        history.append({"candidate": k, "n_demos": len(demos), "dev_val_accuracy": round(acc, 4)})
        log(f"[C] candidate {k}: {len(demos)} demos -> dev-val acc={acc:.3f}")
        if acc > best_acc:
            best, best_acc = cand, acc
    best.name, best.technique = "optimized_bootstrap", "Auto-optimised demos (Arm C, DSPy-style)"
    best.description = (f"Bootstrapped {len(best.examples)} demonstrations (balanced + hard cases) selected by "
                        f"dev-validation accuracy from {n_candidates} candidates.")
    return best, history


class _Rules(BaseModel):
    rules: list[str]


def textgrad_rules(dev: list[dict], llm: LLM, iterations: int = 3, log=print):
    train, val = _split_dev(dev)
    cur = role_guided()
    cur_acc, _, _ = accuracy(cur, val, llm)
    history = [{"iteration": 0, "rules": 0, "dev_val_accuracy": round(cur_acc, 4), "accepted": True}]
    log(f"[D] start dev-val acc={cur_acc:.3f}")
    for it in range(1, iterations + 1):
        _, errs, _ = accuracy(cur, train, llm)
        if not errs:
            break
        s, u = textgrad_feedback(cur.instructions, errs[:12])
        r = llm.complete(s, u, json_mode=True)
        try:
            new_rules = _Rules.model_validate(json.loads(re.sub(r"^```(?:json)?|```$", "", r.text.strip()))).rules
        except Exception:
            new_rules = []
        new_rules = [x for x in new_rules if x not in cur.learned_rules][:5]
        cand = PromptTemplate(**{**cur.to_dict(), "learned_rules": cur.learned_rules + new_rules})
        acc, _, _ = accuracy(cand, val, llm)
        accepted = acc >= cur_acc and bool(new_rules)
        history.append({"iteration": it, "rules": len(cand.learned_rules), "dev_val_accuracy": round(acc, 4),
                        "accepted": accepted, "proposed": new_rules})
        log(f"[D] iter {it}: +{len(new_rules)} rules -> dev-val acc={acc:.3f} ({'kept' if accepted else 'rejected'})")
        if accepted:
            cur, cur_acc = cand, acc
    cur.name, cur.technique = "optimized_textgrad", "Feedback-refined rules (Arm D, TextGrad-style)"
    cur.description = f"Arm A plus {len(cur.learned_rules)} correction rules the model wrote from its own dev errors."
    return cur, history
