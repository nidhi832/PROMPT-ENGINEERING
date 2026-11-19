"""Retrieval-Augmented Generation (RAG) Module for SpendWise.

Indexes domain knowledge (Indian tax rules, 50/30/20 budgeting frameworks,
subscription audits, delivery app markups, emergency fund guidelines)
and retrieves relevant chunks to ground LLM financial advice with verified citations.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import analytics, prompts
from .assistant import grounding_check
from .llm import LLM


@dataclass
class KnowledgeChunk:
    chunk_id: str
    doc_id: str
    doc_title: str
    category: str
    topics: List[str]
    content: str


# Built-in structured knowledge base of personal finance policies & rules
KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "doc_id": "kb_budget_50_30_20",
        "doc_title": "The 50/30/20 Budgeting Rule & Student Benchmarks",
        "category": "Budgeting & Planning",
        "topics": ["50/30/20 rule", "needs vs wants", "savings benchmark", "student budgeting", "roommate expense sharing"],
        "chunks": [
            {
                "chunk_id": "budget_50_30_20_p1",
                "content": (
                    "The 50/30/20 Budgeting Rule allocates after-tax income into three categories: "
                    "50% for Needs (groceries, rent, basic utilities, electricity, essential commute), "
                    "30% for Wants (dining out, Swiggy food delivery, shopping, streaming, cinema), "
                    "and 20% for Savings and Debt Repayment (emergency funds, recurring deposits, investments). "
                    "For college students or young professionals in urban Indian cities, discretionary spending "
                    "(Food delivery + Shopping) frequently exceeds 45% of total outflow, creating cashflow deficits."
                ),
            },
            {
                "chunk_id": "budget_50_30_20_p2",
                "content": (
                    "To transition closer to the 50/30/20 benchmark: (1) Cap food delivery and restaurant outings "
                    "to a strict weekly ceiling; (2) Pool high-speed broadband and household utility subscriptions with roommates; "
                    "(3) Automate a transfer of at least 15-20% of income or allowance into a separate savings account on the 1st of every month."
                ),
            },
        ],
    },
    {
        "doc_id": "kb_tax_80d_80c",
        "doc_title": "Indian Income Tax Deductions: Section 80D, 80C & WFH Expenses",
        "category": "Tax & Regulations",
        "topics": ["Section 80D", "Section 80C", "Section 80E", "health insurance", "preventive checkup", "gym tax deduction", "WFH allowance"],
        "chunks": [
            {
                "chunk_id": "tax_80d_health",
                "content": (
                    "Under Section 80D of the Indian Income Tax Act, individuals can claim deductions up to ₹25,000 per year "
                    "for health insurance premiums paid for self, spouse, and dependent children (up to ₹50,000 for senior citizens). "
                    "Additionally, an amount up to ₹5,000 is allowed within this ₹25,000 cap for annual preventive health check-ups. "
                    "Crucial Rule: Commercial gym, fitness center, or Cult.fit memberships do NOT qualify for tax deductions under Section 80D, "
                    "as fitness subscriptions are classified as personal lifestyle wellness rather than licensed medical insurance or clinical diagnostics."
                ),
            },
            {
                "chunk_id": "tax_80c_80e_education",
                "content": (
                    "Section 80C permits up to ₹1,50,000 in deductions across ELSS mutual funds, PPF, EPF, and tax-saver deposits. "
                    "Section 80E provides a 100% deduction on interest paid on higher education loans with zero upper monetary ceiling "
                    "for up to 8 consecutive assessment years. Work-from-home expenses such as broadband internet and tech equipment "
                    "can be reimbursed tax-free if supported by official employer expense policies and GST invoices."
                ),
            },
        ],
    },
    {
        "doc_id": "kb_food_delivery_optimization",
        "doc_title": "Food & Dining Delivery Optimization: The Swiggy/Zomato Markup Audit",
        "category": "Food & Dining",
        "topics": ["Swiggy", "Zomato", "food delivery fees", "restaurant markup", "meal prep", "dining savings"],
        "chunks": [
            {
                "chunk_id": "food_delivery_markup",
                "content": (
                    "Financial studies of Indian food aggregators (Swiggy, Zomato, Blinkit) demonstrate that food delivery app orders "
                    "incur an effective markup of 18% to 35% over direct dine-in restaurant menu rates when factoring in menu price inflation, "
                    "packaging charges, platform convenience fees (₹6-₹10 per order), surge pricing, and GST. "
                    "A student ordering food delivery 15 times a month at ₹400 per order spends ₹6,000/month, of which ₹1,400 to ₹1,800 "
                    "represents pure delivery overhead and aggregator convenience surcharges."
                ),
            },
            {
                "chunk_id": "food_delivery_mealprep",
                "content": (
                    "The 2-Day Cooking Rule: Replacing just two delivery orders per week with simple home-cooked meals or local mess subscriptions "
                    "trims monthly dining expenditure by ₹2,400 to ₹3,500. Furthermore, Swiggy One or Zomato Gold subscriptions only break even "
                    "if an individual places at least 5 or more orders each month; otherwise the subscription itself constitutes negative cashflow."
                ),
            },
        ],
    },
    {
        "doc_id": "kb_subscription_audit",
        "doc_title": "Subscription & Recurring Service Audit Framework",
        "category": "Subscriptions & Bills",
        "topics": ["zombie subscriptions", "recurring billing", "gym membership audit", "streaming services", "Cult.fit"],
        "chunks": [
            {
                "chunk_id": "sub_zombie_audit",
                "content": (
                    "The 'Zombie Subscription' phenomenon refers to recurring digital services (Netflix, Spotify, Apple iCloud, Disney+ Hotstar, "
                    "gym memberships, auto-renewed cloud trials) that deduct funds on a recurring schedule without regular consumer engagement. "
                    "A bi-annual subscription audit involves: (1) Reviewing bank and credit card statements for recurring auto-debits under ₹1,000; "
                    "(2) Rotating streaming subscriptions sequentially rather than running multiple concurrent platforms."
                ),
            },
            {
                "chunk_id": "sub_gym_cult_utilization",
                "content": (
                    "Gym and fitness membership economics (Cult.fit, Gold's Gym): An annual ₹18,000 to ₹24,000 gym package yields a cost of ₹150-₹200 "
                    "per session only if attended 3+ times per week (120+ sessions/year). When attendance drops below 4 sessions per month, the effective "
                    "cost surges past ₹500 per visit, rendering pay-per-session passes or community running far more cost-effective."
                ),
            },
        ],
    },
    {
        "doc_id": "kb_emergency_fund",
        "doc_title": "Emergency Fund Architecture & Liquidity Guidelines",
        "category": "Savings & Emergency",
        "topics": ["emergency fund", "liquid fund", "credit card trap", "months of expenses", "contingency reserve"],
        "chunks": [
            {
                "chunk_id": "emergency_3_to_6_months",
                "content": (
                    "An emergency contingency reserve must equal 3 to 6 months of non-negotiable living expenses (rent, groceries, utilities, "
                    "medical prescriptions, minimum loan obligations). For a monthly burn rate of ₹35,000, the baseline emergency fund target "
                    "is ₹1,05,000 to ₹2,10,000. Never rely on credit card credit limits as an emergency fund; revolving credit card balances in India "
                    "incur finance charges of 3.5% per month (42% to 48% APR), creating severe debt traps."
                ),
            },
            {
                "chunk_id": "emergency_storage_vehicles",
                "content": (
                    "Emergency reserves must prioritize capital safety and instant liquidity over high yield. Recommended storage vehicles include: "
                    "(1) High-yield savings accounts with scheduled auto-sweep into fixed deposits; (2) Overnight or Liquid mutual funds with instant "
                    "redemption up to ₹50,000; (3) Avoid locking emergency funds in equity mutual funds, ELSS, or real estate where market volatility "
                    "or exit penalties impede immediate crisis withdrawal."
                ),
            },
        ],
    },
]


class KnowledgeRetriever:
    """TF-IDF vector indexer and semantic retriever for personal finance knowledge."""

    def __init__(self, kb_data: List[Dict[str, Any]] = KNOWLEDGE_BASE):
        self.chunks: List[KnowledgeChunk] = []
        for doc in kb_data:
            doc_id = doc["doc_id"]
            doc_title = doc["doc_title"]
            category = doc["category"]
            topics = doc.get("topics", [])
            for c in doc["chunks"]:
                self.chunks.append(
                    KnowledgeChunk(
                        chunk_id=c["chunk_id"],
                        doc_id=doc_id,
                        doc_title=doc_title,
                        category=category,
                        topics=topics,
                        content=c["content"],
                    )
                )

        self.corpus = [
            f"{c.doc_title} {c.category} {' '.join(c.topics)} {c.content}"
            for c in self.chunks
        ]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[KnowledgeChunk, float]]:
        """Retrieve top_k chunks matching query with similarity score."""
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        ranked_indices = sims.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            score = round(float(sims[idx]), 3)
            # Give a modest floor for relevant domain matches
            results.append((self.chunks[idx], score))
        return results

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Return catalog of indexed documents and their summary metadata."""
        catalog = []
        for doc in KNOWLEDGE_BASE:
            catalog.append({
                "doc_id": doc["doc_id"],
                "title": doc["doc_title"],
                "category": doc["category"],
                "topics": doc["topics"],
                "chunk_count": len(doc["chunks"]),
                "summary": doc["chunks"][0]["content"][:160] + "...",
            })
        return catalog


# Singleton instance
_RETRIEVER = KnowledgeRetriever()


def get_retriever() -> KnowledgeRetriever:
    return _RETRIEVER


@dataclass
class RAGResponse:
    answer: str
    citations: List[str]
    retrieved_chunks: List[Dict[str, Any]]
    facts_used: Dict[str, Any]
    grounded: bool
    trace: List[Dict[str, Any]] = field(default_factory=list)


def query_rag(
    question: str,
    df: Optional[pd.DataFrame],
    llm: LLM,
    top_k: int = 3,
) -> RAGResponse:
    """Execute the full RAG pipeline:

    1. Retrieve top-k relevant knowledge chunks.
    2. Extract verified user financial facts from pandas.
    3. Augment system and user prompt with knowledge passages + verified facts.
    4. Call LLM to synthesize a grounded, cited answer.
    5. Perform grounding verification.
    """
    retriever = get_retriever()
    matches = retriever.retrieve(question, top_k=top_k)

    retrieved_info = []
    chunk_blocks = []
    for chunk, score in matches:
        retrieved_info.append({
            "chunk_id": chunk.chunk_id,
            "document": chunk.doc_title,
            "category": chunk.category,
            "similarity": score,
            "text": chunk.content,
        })
        chunk_blocks.append(
            f"[Source: {chunk.doc_title} | Category: {chunk.category} | ID: {chunk.chunk_id}]\n{chunk.content}"
        )

    knowledge_context = "\n\n".join(chunk_blocks)

    # Compute verified user facts from DataFrame if available
    user_facts: Dict[str, Any] = {}
    if df is not None and not df.empty:
        k = analytics.kpis(df)
        user_facts = {
            "total_spent": round(float(k["total"]), 2),
            "transaction_count": int(k["transactions"]),
            "months_recorded": int(k["months"]),
            "monthly_average_spent": round(float(k["monthly_average"]), 2),
        }
        if "category" in df.columns:
            cats = analytics.by_category(df)
            user_facts["top_categories"] = {r.category: round(r.total, 2) for r in cats.head(4).itertuples()}

    system_prompt = (
        "You are SpendWise RAG Advisor, an intelligent personal finance counselor. "
        "You synthesize domain knowledge retrieved from policy documents with verified Python transaction arithmetic. "
        "Rules:\n"
        "1. Base your financial recommendations on the RETRIEVED_KNOWLEDGE passages.\n"
        "2. If referencing user spending figures, use ONLY the VERIFIED_USER_FACTS; do not invent or round differently.\n"
        "3. Explicitly cite the source document titles in your answer.\n"
        "4. Return ONLY valid JSON with keys: 'answer' (string), 'citations' (list of cited document names)."
    )

    user_prompt = f"""RETRIEVED_KNOWLEDGE:
{knowledge_context}

VERIFIED_USER_FACTS (computed by Python arithmetic):
{json.dumps(user_facts, indent=1)}

USER_QUESTION: {question}

Return ONLY valid JSON (no markdown fences):
{{"answer": "<comprehensive 3-5 sentence guidance with citations>", "citations": ["<doc title>", ...]}}"""

    resp = llm.complete(system_prompt, user_prompt, json_mode=True)

    trace = [
        {"step": "rag_retrieval", "retrieved_count": len(matches), "top_similarity": matches[0][1] if matches else 0.0},
        {"step": "llm_synthesis", "tokens": resp.input_tokens + resp.output_tokens, "latency_s": resp.latency_s},
    ]

    try:
        data = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.text.strip()))
        answer = data.get("answer", resp.text)
        citations = data.get("citations", [m[0].doc_title for m in matches])
    except Exception:
        answer = resp.text
        citations = [m[0].doc_title for m in matches]

    # Collect verified numbers from user facts and retrieved knowledge text
    rag_facts: Dict[str, Any] = {**user_facts}
    extracted_nums: List[float] = []
    for c in retrieved_info:
        for m in re.finditer(r"[\d,]+(?:\.\d+)?", c["text"]):
            try:
                extracted_nums.append(float(m.group(0).replace(",", "")))
            except ValueError:
                pass
    rag_facts["retrieved_numbers"] = extracted_nums

    g = grounding_check(answer, rag_facts)

    return RAGResponse(
        answer=answer,
        citations=citations,
        retrieved_chunks=retrieved_info,
        facts_used=user_facts,
        grounded=g.grounded,
        trace=trace,
    )
