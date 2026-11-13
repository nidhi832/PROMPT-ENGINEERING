"""LLM backends: Gemini, Anthropic Claude, any OpenAI-compatible API (Groq, OpenAI, Ollama...), and an
OFFLINE SIMULATOR so the demo never dies on stage (plan section 14: "prepare a recorded or local demo").

The offline simulator is NOT a language model. It is a deterministic stand-in that only uses what is written
in the prompt (category guide words, labelled examples, learned rules) plus a small generic keyword list.
That makes prompt changes visibly change its behaviour, but its scores must never be reported as LLM results.
"""
from __future__ import annotations

import hashlib
import json
import os
import socket
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parent.parent / "results" / "llm_cache.json"

# Cloudflare (in front of Groq and other APIs) blocks Python's default "Python-urllib" User-Agent
# with "error code: 1010". Send our own User-Agent on every request instead.
_opener = urllib.request.build_opener()
_opener.addheaders = [("User-Agent", "SpendWise/1.0 (course project)")]
urllib.request.install_opener(_opener)


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    backend: str
    model: str
    cached: bool = False


def est_tokens(s: str) -> int:
    return max(1, len(s) // 4)


class _Cache:
    def __init__(self, path: Path = CACHE_PATH):
        self.path = path
        self.data: dict = {}
        if path.exists():
            try:
                self.data = json.loads(path.read_text())
            except json.JSONDecodeError:
                self.data = {}

    @staticmethod
    def key(*parts: str) -> str:
        return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()

    def get(self, k):
        return self.data.get(k)

    def put(self, k, v):
        self.data[k] = v
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(self.data))


class LLM:
    name = "base"
    is_real = True
    _on_overloaded_allowed_for_429 = False

    def __init__(self, model: str, use_cache: bool = True, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        self.cache = _Cache() if use_cache else None
        self.calls = 0
        # pin_model=True (set by evaluate.py): never switch to another model. An experiment that silently
        # changes model half-way compares prompts on different models, so it must wait or fail instead.
        self.pin_model = False

    def _call(self, system: str, user: str, json_mode: bool) -> tuple[str, int, int]:
        raise NotImplementedError

    def _on_overloaded(self, err: str) -> bool:
        """Hook: return True if the backend switched to a different model after repeated failures."""
        return False

    def complete(self, system: str, user: str, json_mode: bool = True) -> LLMResponse:
        k = _Cache.key(self.name, self.model, str(self.temperature), str(json_mode), system, user)
        if self.cache and (hit := self.cache.get(k)):
            return LLMResponse(**{**hit, "cached": True, "latency_s": 0.0})
        t0 = time.perf_counter()
        last_err = None
        attempts = 12 if self.pin_model else 10
        for attempt in range(attempts):      # retry with backoff; (unpinned) switch model if one stays overloaded
            try:
                text, tin, tout = self._call(system, user, json_mode)
                break
            except urllib.error.HTTPError as e:
                last_err = f"HTTP {e.code}: {e.read().decode(errors='ignore')[:300]}"
                if e.code not in (429, 500, 502, 503, 504, 529):
                    raise RuntimeError(last_err) from e
                ra = e.headers.get("retry-after") if e.headers else None
                if e.code == 429 and ra and not self._on_overloaded_allowed_for_429:
                    try:
                        wait = min(float(ra), 60.0)
                    except ValueError:
                        wait = 10.0
                    print(f"[{self.name}] rate limited - waiting {wait:.0f}s", flush=True)
                    time.sleep(wait)
                    continue
            except (TimeoutError, socket.timeout, urllib.error.URLError, ConnectionError) as e:
                last_err = f"network/timeout: {e}"
            if attempt >= 1 and not self.pin_model and self._on_overloaded(last_err):
                continue                     # switched to another model - retry immediately
            wait = min(2 ** attempt * 2, 60 if self.pin_model else 20)
            if self.pin_model:
                print(f"[{self.name}] {self.model} busy ({(last_err or '')[:40]}...) - retry {attempt + 1}/{attempts} "
                      f"in {wait}s (model pinned for evaluation)", flush=True)
            time.sleep(wait)
        else:
            raise RuntimeError(f"{self.name} failed after retries: {last_err}")
        self.calls += 1
        resp = LLMResponse(text, tin, tout, round(time.perf_counter() - t0, 3), self.name, self.model)
        if self.cache:
            self.cache.put(k, {kk: vv for kk, vv in resp.__dict__.items() if kk != "cached"})
        return resp


def _post(url: str, body: dict, headers: dict, timeout: int = 150) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class GeminiLLM(LLM):
    name = "gemini"
    _on_overloaded_allowed_for_429 = True

    def __init__(self, model: str | None = None, api_key: str | None = None, **kw):
        super().__init__(model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), **kw)
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
        if not self.api_key:
            raise ValueError("Set GEMINI_API_KEY")
        if len(self.api_key) < 30 or "your" in self.api_key.lower() or "paste" in self.api_key.lower():
            raise ValueError(f"GEMINI_API_KEY looks like a placeholder ('{self.api_key[:12]}...'), not a real key. "
                             "Copy your key from aistudio.google.com/apikey (it starts with AQ.)")

    BASE = "https://generativelanguage.googleapis.com/v1beta"

    def _headers(self):
        # Works for both new auth keys (AQ.…) and legacy keys; keeps the key out of URLs/logs.
        return {"x-goog-api-key": self.api_key.strip()}

    def available_models(self) -> list[str]:
        req = urllib.request.Request(f"{self.BASE}/models?pageSize=200", headers=self._headers())
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        return [m["name"].split("/", 1)[1] for m in d.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])]

    def _on_overloaded(self, err: str) -> bool:
        """Model busy (503/429) or too slow -> move to the next Flash-family model, once per model."""
        tried = getattr(self, "_tried", set()) | {self.model}
        self._tried = tried
        try:
            names = self.available_models()
        except Exception:  # noqa: BLE001
            return False
        prefs = [n for n in names if "flash" in n and n not in tried
                 and not any(x in n for x in ("image", "tts", "live", "audio", "exp", "preview"))]
        prefs.sort(key=lambda n: ("lite" in n, "latest" not in n,
                                  [-int(x) if x.isdigit() else 0 for x in re.split(r"[.-]", n)]))
        if not prefs:
            return False
        print(f"[gemini] {self.model} unavailable ({err[:60]}...) -> switching to {prefs[0]}", flush=True)
        self.model = prefs[0]
        self._tried = tried | {prefs[0]}     # never bounce back to a model already tried
        return True

    def _pick_fallback(self) -> str | None:
        names = self.available_models()
        tried = getattr(self, "_tried", set())
        flash = [n for n in names if "flash" in n and n not in tried
                 and not any(x in n for x in ("lite", "image", "tts", "live", "audio", "exp"))]
        flash.sort(key=lambda n: ("latest" not in n, [-int(x) if x.isdigit() else 0 for x in re.split(r"[.-]", n)]))
        return (flash or names or [None])[0]

    def _call(self, system, user, json_mode):
        cfg = {"temperature": self.temperature}
        if json_mode:
            cfg["responseMimeType"] = "application/json"
        if getattr(self, "_thinking_ok", True):
            # Classification needs no long reasoning; minimal thinking makes calls far faster.
            cfg["thinkingConfig"] = {"thinkingLevel": "minimal"}
        body = {"systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": cfg}
        t0 = time.perf_counter()
        try:
            try:
                d = _post(f"{self.BASE}/models/{self.model}:generateContent", body, self._headers(), timeout=120)
            except urllib.error.HTTPError as e:
                err_body = e.read()
                e.read = lambda b=err_body: b            # keep the body so the real reason is shown later
                if e.code == 400 and "thinking" in err_body.decode(errors="ignore").lower():
                    self._thinking_ok = False            # model doesn't support it -> resend without
                    cfg.pop("thinkingConfig", None)
                    d = _post(f"{self.BASE}/models/{self.model}:generateContent", body, self._headers(), timeout=120)
                else:
                    raise
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            if self.pin_model:
                raise RuntimeError(f"gemini: model '{self.model}' not found. "
                                   "Run: python evaluate.py --backend gemini --list-models") from e
            new = self._pick_fallback()           # model retired/renamed -> use a current Flash model
            if not new or new == self.model:
                raise
            self.model = new
            d = _post(f"{self.BASE}/models/{self.model}:generateContent", body, self._headers())
        parts = d["candidates"][0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        self._ok = getattr(self, "_ok", 0) + 1
        print(f"[gemini] call {self._ok} ok · {self.model} · {time.perf_counter() - t0:.1f}s", flush=True)
        u = d.get("usageMetadata", {})
        return text, u.get("promptTokenCount", est_tokens(system + user)), u.get("candidatesTokenCount", est_tokens(text))


class AnthropicLLM(LLM):
    name = "anthropic"

    def __init__(self, model: str | None = None, api_key: str | None = None, **kw):
        super().__init__(model or os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5"), **kw)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Set ANTHROPIC_API_KEY")

    def _call(self, system, user, json_mode):
        body = {"model": self.model, "max_tokens": 4096, "temperature": self.temperature,
                "system": system, "messages": [{"role": "user", "content": user}]}
        d = _post("https://api.anthropic.com/v1/messages", body,
                  {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"})
        text = "".join(b.get("text", "") for b in d["content"])
        return text, d["usage"]["input_tokens"], d["usage"]["output_tokens"]


class OpenAICompatLLM(LLM):
    """OpenAI, Groq (free tier), Together, OpenRouter, local Ollama - anything with /chat/completions."""
    name = "openai-compatible"

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str | None = None, **kw):
        super().__init__(model or os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile"), **kw)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")).rstrip("/")

    PREFERRED = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "meta-llama/llama-4-maverick-17b-128e-instruct",
                 "meta-llama/llama-4-scout-17b-16e-instruct", "openai/gpt-oss-20b", "llama-3.1-8b-instant"]

    def _current_model(self) -> str | None:
        req = urllib.request.Request(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ids = [m["id"] for m in json.loads(r.read()).get("data", [])]
        for p in self.PREFERRED:
            if p in ids and p != self.model:
                return p
        chat = [i for i in ids if not any(x in i for x in ("whisper", "tts", "guard", "embed", "playai", "orpheus"))]
        return next((i for i in chat if i != self.model), None)

    def _call(self, system, user, json_mode):
        body = {"model": self.model, "temperature": self.temperature,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        hdr = {"Authorization": f"Bearer {self.api_key}"}
        t0 = time.perf_counter()
        try:
            d = _post(f"{self.base_url}/chat/completions", body, hdr)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            e.read = lambda m=msg: m.encode()
            retired = e.code == 404 or (e.code == 400 and ("decommission" in msg or "model" in msg.lower()
                                                            and "not" in msg.lower() and "exist" in msg.lower()))
            if not retired:
                raise
            if self.pin_model:
                raise RuntimeError(f"{self.name}: model '{self.model}' not available. "
                                   "Run: python evaluate.py --backend openai-compatible --list-models") from e
            new = self._current_model()
            if not new:
                raise
            print(f"[{self.name}] model {self.model} unavailable -> using {new}", flush=True)
            self.model = body["model"] = new
            d = _post(f"{self.base_url}/chat/completions", body, hdr)
        self._ok = getattr(self, "_ok", 0) + 1
        print(f"[{self.name}] call {self._ok} ok · {self.model} · {time.perf_counter() - t0:.1f}s", flush=True)
        text = d["choices"][0]["message"]["content"]
        u = d.get("usage", {})
        return text, u.get("prompt_tokens", est_tokens(system + user)), u.get("completion_tokens", est_tokens(text))


# ============================================================================ offline simulator

GENERIC_LEXICON = {
    "Food": ["food", "restaurant", "pizza", "coffee", "cafe", "grocer", "bakery", "canteen", "milk", "bread",
             "chai", "burger", "meal", "lunch", "dinner", "eats", "kitchen"],
    "Transport": ["taxi", "cab", "auto", "metro", "petrol", "fuel", "train", "bus", "flight", "airline", "toll",
                  "parking"],
    "Shopping": ["store", "shop", "electronics", "fashion", "clothing", "mall", "mart", "retail"],
    "Bills": ["bill", "electricity", "rent", "recharge", "postpaid", "broadband", "internet", "water", "lpg",
              "cylinder", "utility"],
    "Entertainment": ["movie", "cinema", "music", "game", "concert", "ticket", "show", "streaming"],
    "Health": ["pharmacy", "medic", "doctor", "clinic", "hospital", "dental", "health", "gym", "fitness"],
    "Education": ["course", "book", "exam", "tuition", "school", "college", "university", "stationery",
                  "library", "fee"],
    "Other": ["atm", "cash", "transfer", "gift", "donation", "salon", "haircut", "laundry"],
}
STOP = {"the", "and", "for", "order", "upi", "with", "from", "payment", "purchase", "like", "anything", "online",
        "membership", "subscription", "subscriptions", "service", "services", "personal", "unclear", "goods",
        "people", "orders", "fees", "delivery", "store", "transfers"}


def _tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z][a-z0-9.&]+", s.lower()) if len(t) >= 3 and t not in STOP]


class OfflineSimulator(LLM):
    name = "offline-simulator"
    is_real = False

    def __init__(self, **kw):
        kw.setdefault("use_cache", False)
        super().__init__("prompt-conditioned-rules-v1", **kw)

    def complete(self, system, user, json_mode=True):
        t0 = time.perf_counter()
        from . import prompts as P
        if "Transactions (id | description):" in user:
            text = self._categorise(user)
        elif system == P.QUERY_ROUTER_SYSTEM:
            text = self._route(user)
        elif system == P.ANSWER_SYSTEM:
            text = self._answer(user)
        elif system == P.BUDGET_SYSTEM:
            text = self._budget(user)
        elif system == P.REPORT_SYSTEM:
            text = self._report(user)
        elif system == P.FEEDBACK_SYSTEM:
            text = self._feedback(user)
        else:
            text = "{}"
        self.calls += 1
        return LLMResponse(text, est_tokens(system + user), est_tokens(text),
                           round(time.perf_counter() - t0, 4), self.name, self.model)

    # -- categorisation: scores categories using ONLY knowledge present in the prompt + generic lexicon
    def _categorise(self, user: str) -> str:
        from .schemas import CATEGORIES
        guide = {c: [] for c in CATEGORIES}
        for c, words in re.findall(r"^- (\w+): (.+)$", user, flags=re.M):
            if c in guide:
                guide[c] = _tokens(words)
        examples = re.findall(r'^Example: "(.+)" -> (\w+)$', user, flags=re.M)
        rules = re.findall(r'^Rule: .*?"(.+?)" -> (\w+)', user, flags=re.M)
        ex_tok: dict[str, dict[str, float]] = {}
        for d, c in examples:
            for t in set(_tokens(d)):
                ex_tok.setdefault(t, {}).setdefault(c, 0)
                ex_tok[t][c] += 1
        items = re.findall(r"^(T\w+) \| (.+)$", user.split("Transactions (id | description):")[1], flags=re.M)
        json_mode = "Return ONLY valid JSON" in user
        out = []
        for tid, desc in items:
            low, toks = desc.lower(), _tokens(desc)
            score = {c: 0.0 for c in CATEGORIES}
            why: dict[str, str] = {}
            for c in CATEGORIES:
                for kw in GENERIC_LEXICON[c]:
                    if any(t.startswith(kw) for t in toks):
                        score[c] += 1; why.setdefault(c, f"generic keyword '{kw}'")
                for kw in guide[c]:
                    if kw in toks:
                        score[c] += 1.5; why.setdefault(c, f"category guide mentions '{kw}'")
            for t in toks:
                for c, n in ex_tok.get(t, {}).items():
                    score[c] += 2 * n / sum(ex_tok[t].values()); why.setdefault(c, f"similar to example '{t}'")
            for phrase, c in rules:
                if c in score and phrase.lower() in low:
                    score[c] += 6; why[c] = f"learned rule '{phrase}'"
            ranked = sorted(score.items(), key=lambda kv: -kv[1])
            (best, s1), (_, s2) = ranked[0], ranked[1]
            if s1 == 0:
                best, conf, expl = "Other", 0.3, "Merchant not recognised from the description"
            else:
                conf = round(min(0.97, max(0.3, s1 / (s1 + s2 + 0.5))), 2)
                expl = f"Matched {why.get(best, 'keywords')}"
            out.append({"id": tid, "category": best, "confidence": conf, "explanation": expl,
                        "needs_review": conf < 0.6})
        if json_mode:
            return json.dumps({"results": out})
        return "\n".join(f"{o['id']}: {o['category']}" for o in out)

    def _route(self, user: str) -> str:
        months = re.search(r"Available months \(YYYY-MM\): (.+)", user).group(1).split(", ")
        q = user.rsplit("Question:", 1)[1].strip().lower()
        from .schemas import CATEGORIES
        cat = next((c for c in CATEGORIES if c.lower() in q), None)
        syn = {"groceries": "Food", "eating": "Food", "restaurants": "Food", "travel": "Transport", "cab": "Transport",
               "uber": "Transport", "movies": "Entertainment", "subscriptions": "Entertainment", "rent": "Bills",
               "medicine": "Health", "courses": "Education", "clothes": "Shopping"}
        cat = cat or next((c for w, c in syn.items() if w in q), None)
        found = []
        for m in months:
            import calendar
            name = calendar.month_name[int(m[5:])].lower()
            if name in q or name[:3] + " " in q + " ":
                found.append(m)
        if re.search(r"last month|this month|latest month|recent month", q) and not found:
            found.append(months[-1])
        n = int(m.group(1)) if (m := re.search(r"\b(\d{1,2})\b", q)) else 5
        if re.search(r"invest|stock|crypto|salary|income|loan|credit score|mutual fund", q):
            intent = "unsupported"
        elif re.search(r"compare|vs\.?|versus|than|change|differ", q):
            intent = "compare_months"
            if len(found) < 2 and len(months) >= 2:
                found = [found[0] if found else months[-1]]
                found.append(months[months.index(found[0]) - 1] if months.index(found[0]) > 0 else months[-1])
        elif re.search(r"(biggest|largest|most expensive|highest).*(transaction|purchase|payment|expense)", q):
            intent = "largest"
        elif re.search(r"\btop\b|most|biggest|highest|which categor", q):
            intent = "top_categories"
        elif re.search(r"how many|number of|count", q):
            intent = "count"
        elif re.search(r"average|avg|typical", q):
            intent = "average"
        elif re.search(r"breakdown|by category|split|where.*money|categories", q):
            intent = "by_category"
        elif re.search(r"\blist\b|\bshow\b|which transactions", q):
            intent = "list"
        else:
            intent = "total"
        return json.dumps({"intent": intent, "category": cat, "month": found[0] if found else None,
                           "month_b": found[1] if len(found) > 1 else None, "n": min(max(n, 1), 20)})

    def _answer(self, user: str) -> str:
        r = json.loads(user.split("VERIFIED_RESULT (computed by Python):\n", 1)[1].rsplit("\n\nAnswer in", 1)[0])
        scope = r.get("scope", "all your data")
        it = r.get("intent")
        if it == "unsupported":
            return ("I can only answer questions about the transactions you uploaded. Your data has no information "
                    "about income, investments or loans, so I can't answer that without guessing.")
        if r.get("matching_transactions", 1) == 0:
            return f"I couldn't find any transactions for {scope}, so there is nothing to total."
        if it == "total":
            return f"You spent ₹{r['total']:,.2f} on {scope} across {r['matching_transactions']} transactions."
        if it == "count":
            return f"There were {r['matching_transactions']} transactions for {scope}, totalling ₹{r['total']:,.2f}."
        if it == "average":
            return (f"Your average transaction for {scope} was ₹{r['average']:,.2f}, "
                    f"over {r['matching_transactions']} transactions.")
        if it in ("by_category", "top_categories"):
            items = list(r["categories"].items())
            lead = ", ".join(f"{c} ₹{v:,.2f}" for c, v in items[:3])
            return f"For {scope}, your biggest categories were {lead}. Total spending was ₹{r['total']:,.2f}."
        if it == "compare_months":
            a, b = r["month"], r["month_b"]
            direction = "more" if r["difference"] > 0 else "less"
            return (f"You spent ₹{r['total_month']:,.2f} in {a} versus ₹{r['total_month_b']:,.2f} in {b}"
                    f" ({r['scope_category']}) - that's ₹{abs(r['difference']):,.2f} {direction} "
                    f"({r['difference_pct']:+.1f}%).")
        if it in ("largest", "list"):
            rows = r["transactions"][:3]
            lead = "; ".join(f"{t['description']} ₹{t['amount']:,.2f} on {t['date']}" for t in rows)
            return f"Here are the matching transactions for {scope}: {lead}."
        return "Here is what I found in your data."

    def _budget(self, user: str) -> str:
        f = json.loads(user.split("VERIFIED_FACTS (computed by Python, amounts in ₹):\n", 1)[1].split("\n\nGive up to", 1)[0])
        avg = f["average_monthly_by_category"]
        missing = []
        if not f.get("user_monthly_budget") and not f.get("user_monthly_savings_goal"):
            missing.append("A monthly budget or savings goal, so suggestions can be sized to your target.")
        if f.get("user_monthly_savings_goal") and not f.get("user_monthly_income"):
            missing.append("Your monthly income, to check whether the savings goal is reachable.")
        disc = [(c, v) for c, v in avg.items() if c in ("Food", "Shopping", "Entertainment", "Transport")]
        disc += [(c, v) for c, v in avg.items() if c == "Other"]   # 'Other' only if fewer than 3 flexible ones
        tips = {"Food": ("Plan 2 home-cooked days a week", "Food delivery and eating out is your largest flexible cost; swapping a few orders for cooking usually trims it."),
                "Shopping": ("Add a 48-hour rule for purchases", "Waiting two days before non-essential orders cuts impulse buys."),
                "Entertainment": ("Audit your subscriptions", "Keep the streaming and music plans you actually used this month and pause the rest."),
                "Transport": ("Swap some cab rides for metro or bus", "Short cab and auto trips add up; public transport covers many routes for less."),
                "Other": ("Track transfers and cash", "Cash and UPI transfers are hard to trace; noting what they were for makes them easier to control.")}
        sugg = []
        for c, v in disc[:3]:
            t, d = tips[c]
            sugg.append({"title": t, "detail": f"{d} You average ₹{v:,.2f} a month on {c}.", "category": c,
                         "estimated_monthly_saving": round(v * 0.15, 2)})
        gap = f.get("gap_vs_budget", f.get("gap_vs_goal"))
        if gap is None:
            summary = f"You average ₹{f['average_monthly_total']:,.2f} a month over {f['months_of_data']} months."
        elif gap > 0:
            summary = (f"You average ₹{f['average_monthly_total']:,.2f} a month, which is ₹{gap:,.2f} above your "
                       "target. The suggestions below focus on your largest flexible categories.")
        else:
            summary = (f"You average ₹{f['average_monthly_total']:,.2f} a month, ₹{abs(gap):,.2f} under your "
                       "target - nice work. These ideas can grow the buffer further.")
        return json.dumps({"summary": summary, "suggestions": sugg, "missing_information": missing})

    def _report(self, user: str) -> str:
        f = json.loads(user.split("amounts in ₹):\n", 1)[1].split("\n\nWrite a report.", 1)[0])
        cats = list(f["category_totals"].items())
        obs = [f"You spent ₹{f['total_spent']:,.2f} across {f['transaction_count']} transactions in {f['month_name']}.",
               f"{cats[0][0]} was the largest category at ₹{cats[0][1]:,.2f} ({f['category_share_pct'][cats[0][0]]}% of spending).",
               f"Your single largest transaction was {f['largest_transaction']['description']} at ₹{f['largest_transaction']['amount']:,.2f}."]
        if "change_vs_previous_pct" in f:
            ch = f["category_change_vs_previous"]
            up = max(ch.items(), key=lambda kv: kv[1])
            obs.append(f"Total spending changed {f['change_vs_previous_pct']:+.1f}% versus {f.get('previous_month_name', f['previous_month'])}"
                       f" (₹{f['previous_total']:,.2f}).")
            if up[1] > 0:
                obs.append(f"{up[0]} rose the most, up ₹{up[1]:,.2f} on the previous month.")
        flex = next((c for c, _ in cats if c in ("Food", "Shopping", "Entertainment", "Transport")), cats[0][0])
        head = (f"{f['month_name']}: ₹{f['total_spent']:,.2f} spent, led by {cats[0][0]}")
        return json.dumps({"headline": head, "observations": obs[:5],
                           "next_steps": [f"Set a weekly cap for {flex} and check it every Sunday.",
                                          "Review transactions flagged for review so category totals stay accurate.",
                                          "Compare next month's report against this one to track progress."]})

    def _feedback(self, user: str) -> str:
        rules = []
        for d, c in re.findall(r'^- "(.+)" predicted \w+, correct (\w+)$', user, flags=re.M):
            toks = _tokens(re.sub(r"^upi/\d+/", "", d.lower()))
            if toks:
                phrase = " ".join(toks[:2]) if len(toks) > 1 and len(toks[0]) < 8 else toks[0]
                r = f'descriptions containing "{phrase}" -> {c}'
                if r not in rules:
                    rules.append(r)
        return json.dumps({"rules": rules[:5]})


def available_backends() -> list[str]:
    out = []
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        out.append("gemini")
    if os.getenv("ANTHROPIC_API_KEY"):
        out.append("anthropic")
    if os.getenv("OPENAI_API_KEY"):
        out.append("openai-compatible")
    out.append("offline-simulator")
    return out


def make_llm(backend: str, model: str | None = None, api_key: str | None = None, **kw) -> LLM:
    if backend == "gemini":
        return GeminiLLM(model=model, api_key=api_key, **kw)
    if backend == "anthropic":
        return AnthropicLLM(model=model, api_key=api_key, **kw)
    if backend == "openai-compatible":
        return OpenAICompatLLM(model=model, api_key=api_key, base_url=kw.pop("base_url", None), **kw)
    return OfflineSimulator()
