"""Run the full prompt-comparison experiment from the command line.

    python evaluate.py --backend gemini              # real results (needs GEMINI_API_KEY)
    python evaluate.py --backend anthropic           # needs ANTHROPIC_API_KEY
    python evaluate.py --backend openai-compatible   # e.g. Groq: OPENAI_API_KEY + OPENAI_BASE_URL
    python evaluate.py --backend offline-simulator   # pipeline check only - NOT LLM results
"""
import argparse

from spendwise.evaluation import run_evaluation
from spendwise.llm import make_llm

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="offline-simulator",
                    choices=["gemini", "anthropic", "openai-compatible", "offline-simulator"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--no-optimise", action="store_true")
    a = ap.parse_args()
    res = run_evaluation(make_llm(a.backend, a.model), optimise=not a.no_optimise)
    print(f"\n{'arm':<22}{'acc':>7}{'F1':>7}{'amb':>7}{'json':>7}{'calls':>7}{'tok/txn':>9}")
    for r in res["arms"]:
        print(f"{r['name']:<22}{r['accuracy']:>7.3f}{r['macro_f1']:>7.3f}{r['ambiguous_accuracy']:>7.3f}"
              f"{r['json_validity']:>7.2f}{r['calls']:>7}{r['tokens_per_txn']:>9}")
    if not res["is_real_llm"]:
        print("\nNOTE: offline simulator = pipeline check, not LLM results. Re-run with a real backend.")
