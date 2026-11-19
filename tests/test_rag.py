"""Unit tests for SpendWise Retrieval-Augmented Generation (RAG) module."""
import pytest
from spendwise import rag, llm, data


def test_retriever_initialization():
    retriever = rag.get_retriever()
    assert len(retriever.chunks) >= 8
    docs = retriever.get_all_documents()
    assert len(docs) >= 5
    titles = [d["title"] for d in docs]
    assert any("80D" in t or "Tax" in t for t in titles)
    assert any("50/30/20" in t for t in titles)


def test_semantic_retrieval_relevance():
    retriever = rag.get_retriever()
    # Query about Section 80D and health/gym
    matches_tax = retriever.retrieve("Can I claim Section 80D tax deduction for Cult.fit gym membership?", top_k=2)
    assert len(matches_tax) == 2
    top_chunk, score = matches_tax[0]
    assert "80D" in top_chunk.doc_title or "Tax" in top_chunk.category
    assert score > 0.1

    # Query about food delivery
    matches_food = retriever.retrieve("How much do Swiggy and Zomato markup food prices?", top_k=2)
    top_chunk_food, score_food = matches_food[0]
    assert "Food" in top_chunk_food.category or "Swiggy" in top_chunk_food.doc_title
    assert score_food > 0.1


def test_rag_end_to_end_synthesis():
    simulator = llm.make_llm("offline-simulator")
    df, _ = data.load_transactions("data/sample_expenses.csv")
    
    # 80D Gym query
    res = rag.query_rag("Is Cult.fit membership tax deductible under 80D?", df, simulator)
    assert "Section 80D" in res.answer
    assert "Cult.fit" in res.answer or "gym" in res.answer.lower()
    assert len(res.citations) > 0
    assert len(res.retrieved_chunks) > 0
    assert res.grounded is True

    # 50/30/20 query with facts
    res_budget = rag.query_rag("How does the 50/30/20 rule apply to my spending?", df, simulator)
    assert "50/30/20" in res_budget.answer
    assert len(res_budget.citations) > 0
    assert "monthly_average_spent" in res_budget.facts_used
    assert res_budget.grounded is True
