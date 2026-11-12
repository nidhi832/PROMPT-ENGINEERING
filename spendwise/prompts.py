"""SpendWise prompt library.

Every prompt the system sends is defined here, versioned, and tagged with the technique it demonstrates.
Categorisation strategies (the experiment arms):

  zero_shot_plain   Zero-shot, free text output             (baseline, shows why JSON matters - RQ2)
  zero_shot_json    Zero-shot + constrained JSON schema     (RQ1, RQ2)
  role_guided       Role prompt + category guide + JSON     (Arm A: best manual prompt)
  few_shot          Arm A + labelled demonstrations         (Arm B)
  optimized_*       Produced by spendwise.optimizer         (Arm C: DSPy-style bootstrap, Arm D: TextGrad-style)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .schemas import CATEGORIES

CATS = ", ".join(CATEGORIES)

JSON_SCHEMA_TEXT = """Return ONLY valid JSON (no markdown fences) with this exact shape:
{"results": [{"id": "<transaction id>", "category": "<one allowed category>", "confidence": <0.0-1.0>,
  "explanation": "<max 15 words, based only on the description>", "needs_review": <true|false>}]}
Return one result per transaction, in the same order, using the same ids."""

CATEGORY_GUIDE = """Category guide:
- Food: restaurants, cafes, groceries, bakeries, canteens, food delivery (Swiggy, Zomato, Blinkit, BigBasket)
- Transport: cabs and autos (Uber, Ola, Rapido), metro, bus, train (IRCTC), flights, fuel, petrol
- Shopping: clothing, electronics, online retail orders (Myntra, Flipkart), sports goods, beauty, furniture
- Bills: rent, electricity, water, gas cylinder, mobile recharge or postpaid, broadband internet
- Entertainment: streaming and music subscriptions (Netflix, Spotify), movies, cinema, games, concerts, events
- Health: pharmacy, medicines, doctor, clinic, gym or fitness membership
- Education: courses (Coursera, Udemy), books, exam or tuition fees, stationery, library
- Other: cash withdrawals, transfers to people, gifts, donations, personal services, anything unclear"""

ROLE = ("You are SpendWise, a careful personal-finance categorisation assistant. You label bank transactions "
        "for a student budgeting app. You never guess details that are not in the description.")

RULES = """Rules:
1. Choose exactly one category from: {cats}.
2. Use the transaction description only. Do not infer facts that are not present.
3. If the merchant could reasonably belong to more than one category, or is unrecognisable, choose the most
   likely category, lower the confidence below 0.6 and set needs_review to true.
4. Payments to people (UPI transfer to a name) and cash withdrawals are Other.""".format(cats=CATS)


@dataclass
class PromptTemplate:
    name: str
    technique: str
    description: str
    system: str
    instructions: str
    json_mode: bool = True
    examples: list[tuple[str, str]] = field(default_factory=list)   # (description, category)
    learned_rules: list[str] = field(default_factory=list)          # TextGrad-style feedback rules

    def render(self, items: list[dict]) -> tuple[str, str]:
        """items: [{"id":..., "description":...}] -> (system, user)"""
        parts = [self.instructions]
        if self.learned_rules:
            parts.append("Learned corrections (from validation errors):\n" +
                         "\n".join(f"Rule: {r}" for r in self.learned_rules))
        if self.examples:
            parts.append("Labelled examples:\n" +
                         "\n".join(f'Example: "{d}" -> {c}' for d, c in self.examples))
        lines = "\n".join(f'{it["id"]} | {it["description"]}' for it in items)
        parts.append(f"Transactions (id | description):\n{lines}")
        return self.system, "\n\n".join(parts)

    def to_dict(self) -> dict:
        return {"name": self.name, "technique": self.technique, "description": self.description,
                "system": self.system, "instructions": self.instructions, "json_mode": self.json_mode,
                "examples": self.examples, "learned_rules": self.learned_rules}

    @classmethod
    def from_dict(cls, d: dict) -> "PromptTemplate":
        d = dict(d)
        d["examples"] = [tuple(e) for e in d.get("examples", [])]
        return cls(**d)


def zero_shot_plain() -> PromptTemplate:
    return PromptTemplate(
        name="zero_shot_plain", technique="Zero-shot (free text)",
        description="Bare instruction, no schema, no examples. Output must be scraped with regex.",
        system="You are a helpful assistant.",
        instructions=f"Categorise each transaction into one of: {CATS}.\n"
                     "Answer with one line per transaction in the form `id: Category`.",
        json_mode=False)


def zero_shot_json() -> PromptTemplate:
    return PromptTemplate(
        name="zero_shot_json", technique="Zero-shot + JSON schema",
        description="Same bare instruction, but the output is constrained to a validated JSON schema.",
        system="You are a helpful assistant.",
        instructions=f"Categorise each transaction into one of: {CATS}.\n\n{JSON_SCHEMA_TEXT}")


def role_guided() -> PromptTemplate:
    return PromptTemplate(
        name="role_guided", technique="Role + guide + rules + JSON (Arm A: best manual)",
        description="Persona, category definitions, explicit ambiguity rules and the JSON schema.",
        system=ROLE,
        instructions=f"{CATEGORY_GUIDE}\n\n{RULES}\n\n{JSON_SCHEMA_TEXT}")


def few_shot(examples: list[tuple[str, str]]) -> PromptTemplate:
    p = role_guided()
    p.name, p.technique = "few_shot", "Few-shot (Arm B)"
    p.description = f"Arm A plus {len(examples)} labelled demonstrations covering every category."
    p.examples = list(examples)
    return p


def pick_balanced_examples(dev_rows: list[dict], per_category: int = 2, seed: int = 7) -> list[tuple[str, str]]:
    """Deterministic, category-balanced demonstrations drawn ONLY from the dev split."""
    import random
    rng = random.Random(seed)
    out = []
    for cat in CATEGORIES:
        pool = [r for r in dev_rows if r["category"] == cat]
        rng.shuffle(pool)
        out += [(r["description"], cat) for r in pool[:per_category]]
    return out


# ---------------------------------------------------------------- downstream prompts (prompt chain)

QUERY_ROUTER_SYSTEM = ("You convert a user's question about their own expenses into a structured query. "
                       "You never answer the question yourself and never compute numbers.")


def query_router(question: str, months: list[str], categories: list[str]) -> tuple[str, str]:
    user = f"""Available months (YYYY-MM): {", ".join(months)}
Available categories: {", ".join(categories)}

Map the question to ONE intent:
- total: total spent (optionally in a month and/or category)
- by_category: breakdown of spending by category (optionally for a month)
- top_categories: the n biggest categories
- compare_months: compare month vs month_b (optionally for a category)
- largest: the n largest transactions (optionally filtered)
- count: number of transactions (optionally filtered)
- average: average transaction amount (optionally filtered)
- list: list transactions matching filters
- unsupported: the question cannot be answered from transaction data (e.g. investments, income, future prices)

Resolve month names to YYYY-MM using the available months ("last month" = the latest available month).
Return ONLY JSON: {{"intent": ..., "category": <category or null>, "month": <YYYY-MM or null>,
"month_b": <YYYY-MM or null>, "n": <int, default 5>}}

Question: {question}"""
    return QUERY_ROUTER_SYSTEM, user


ANSWER_SYSTEM = ("You are SpendWise, a friendly budgeting assistant. You explain verified numbers in plain "
                 "language. Use ONLY the numbers in VERIFIED_RESULT; never calculate, round differently or "
                 "invent figures, merchants or dates. Currency is Indian rupees (₹).")


def grounded_answer(question: str, result: dict) -> tuple[str, str]:
    user = (f"Question: {question}\n\nVERIFIED_RESULT (computed by Python):\n{json.dumps(result, default=str, indent=1)}"
            "\n\nAnswer in 2-4 short sentences. Quote amounts exactly as given. If the result is empty or the "
            "intent is unsupported, say what data is missing instead of guessing.")
    return ANSWER_SYSTEM, user


BUDGET_SYSTEM = ("You are a careful budgeting assistant. Use only the supplied spending totals and the user's "
                 "stated budget or goal. Do not invent income, debts or financial circumstances. Give practical, "
                 "non-judgmental suggestions. This is educational guidance, not financial advice.")


def budget_suggestions(facts: dict) -> tuple[str, str]:
    user = f"""VERIFIED_FACTS (computed by Python, amounts in ₹):
{json.dumps(facts, indent=1)}

Give up to three suggestions. Each suggestion must reference a category that appears in the facts and its
estimated_monthly_saving must not exceed that category's average monthly total. If the data or the user's
goal is insufficient, list what is missing in missing_information.
Return ONLY JSON: {{"summary": str, "suggestions": [{{"title": str, "detail": str, "category": str,
"estimated_monthly_saving": number}}], "missing_information": [str]}}"""
    return BUDGET_SYSTEM, user


REPORT_SYSTEM = ("You write short, factual monthly spending reports for a student budgeting app. Use only the "
                 "verified facts provided. Never invent numbers, merchants or reasons for spending.")


def monthly_report(facts: dict) -> tuple[str, str]:
    user = f"""VERIFIED_FACTS for {facts['month_name']} (computed by Python, amounts in ₹):
{json.dumps(facts, indent=1)}

Write a report. Quote amounts exactly as they appear in the facts.
Return ONLY JSON: {{"headline": str (max 15 words), "observations": [3-5 strings],
"next_steps": [2-3 practical strings]}}"""
    return REPORT_SYSTEM, user


FEEDBACK_SYSTEM = ("You are a prompt optimiser. You study a classifier's mistakes on a validation set and write "
                   "short, general correction rules that will fix them without overfitting.")


def textgrad_feedback(instructions: str, errors: list[dict]) -> tuple[str, str]:
    errs = "\n".join(f'- "{e["description"]}" predicted {e["predicted"]}, correct {e["category"]}' for e in errors)
    user = f"""Current categorisation prompt:
---
{instructions}
---
Validation mistakes:
{errs}

Write at most 5 correction rules in the form: descriptions containing "<lowercase merchant phrase>" -> <Category>
Return ONLY JSON: {{"rules": [str]}}"""
    return FEEDBACK_SYSTEM, user


def builtin_strategies(dev_rows: list[dict]) -> dict[str, PromptTemplate]:
    return {p.name: p for p in [zero_shot_plain(), zero_shot_json(), role_guided(),
                                few_shot(pick_balanced_examples(dev_rows))]}
