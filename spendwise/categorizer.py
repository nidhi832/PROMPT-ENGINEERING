"""Smart categorisation (Feature 2): batch prompts -> JSON -> Pydantic validation -> one repair retry."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from pydantic import ValidationError

from .llm import LLM
from .prompts import PromptTemplate
from .schemas import CATEGORIES, BatchCategorization, CategoryResult

BATCH = 20


@dataclass
class CatStats:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    items: int = 0
    strict_valid: int = 0        # items whose FIRST response parsed as schema-valid JSON
    repaired: int = 0            # items recovered by regex scraping or a retry
    failed: int = 0              # items that never produced a usable label -> Other + review
    errors: list[str] = field(default_factory=list)

    def add(self, r):
        self.calls += 1
        self.input_tokens += r.input_tokens
        self.output_tokens += r.output_tokens
        self.latency_s += r.latency_s


def _strip_fences(t: str) -> str:
    t = t.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    return t


def parse_strict(text: str, ids: list[str]) -> dict[str, CategoryResult] | None:
    """Strict path: the whole response must be the JSON schema, with every id present."""
    try:
        batch = BatchCategorization.model_validate(json.loads(_strip_fences(text)))
    except (json.JSONDecodeError, ValidationError):
        return None
    got = {r.id: r for r in batch.results}
    return got if set(ids) <= set(got) else None


def parse_lenient(text: str, ids: list[str]) -> dict[str, CategoryResult]:
    """Fallback: salvage per-item JSON objects or `id: Category` lines. Marked as needing review."""
    out: dict[str, CategoryResult] = {}
    try:
        data = json.loads(_strip_fences(text))
        for r in data.get("results", []) if isinstance(data, dict) else data:
            try:
                cr = CategoryResult.model_validate(r)
                out[cr.id] = cr
            except ValidationError:
                pass
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    for tid, cat in re.findall(r"(T\w+)\s*[:|\-]+\s*\**\s*([A-Za-z]+)", text):
        cat = cat.capitalize()
        if tid in ids and tid not in out and cat in CATEGORIES:
            out[tid] = CategoryResult(id=tid, category=cat, confidence=0.5,
                                      explanation="Parsed from free-text output (no confidence given)",
                                      needs_review=False)
    return out


def categorise(items: list[dict], prompt: PromptTemplate, llm: LLM, batch_size: int = BATCH,
               progress=None) -> tuple[list[CategoryResult], CatStats]:
    """items: [{"id", "description"}]. Returns one CategoryResult per item, in order."""
    stats = CatStats(items=len(items))
    results: dict[str, CategoryResult] = {}
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    for bi, batch in enumerate(batches):
        ids = [it["id"] for it in batch]
        system, user = prompt.render(batch)
        r = llm.complete(system, user, json_mode=prompt.json_mode)
        stats.add(r)
        got = parse_strict(r.text, ids) if prompt.json_mode else None
        if got:
            stats.strict_valid += len(ids)
        else:
            got = parse_lenient(r.text, ids)
            missing = [i for i in ids if i not in got]
            if missing and prompt.json_mode:   # one repair retry, only for the missing items
                retry_batch = [it for it in batch if it["id"] in missing]
                s2, u2 = prompt.render(retry_batch)
                u2 += "\n\nYour previous answer was not valid JSON for the schema. Return ONLY the JSON object."
                r2 = llm.complete(s2, u2, json_mode=True)
                stats.add(r2)
                got.update(parse_strict(r2.text, missing) or parse_lenient(r2.text, missing))
            stats.repaired += sum(1 for i in ids if i in got)
        for it in batch:
            if it["id"] in got:
                results[it["id"]] = got[it["id"]]
            else:
                stats.failed += 1
                results[it["id"]] = CategoryResult(id=it["id"], category="Other", confidence=0.0,
                                                   explanation="Model output unusable - flagged for review",
                                                   needs_review=True)
        if progress:
            progress((bi + 1) / len(batches))
    return [results[it["id"]] for it in items], stats
