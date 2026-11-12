import io

import pandas as pd

from spendwise import analytics, assistant
from spendwise.categorizer import categorise, parse_lenient, parse_strict
from spendwise.data import load_transactions
from spendwise.llm import make_llm
from spendwise.prompts import builtin_strategies
from spendwise.schemas import QueryIntent

CSV = b"""Txn Date,Narration,Debit
2026-10-01,Swiggy order #1234,"1,250.50"
2026-10-02,Uber ride,-300
bad-date,Netflix,499
2026-10-05,,100
2026-10-06,Apollo Pharmacy,abc
2026-09-03,Netflix subscription,499
"""


def test_import_validation_maps_columns_and_rejects_bad_rows():
    df, rep = load_transactions(io.BytesIO(CSV))
    assert list(df["description"]) == ["Netflix subscription", "Swiggy order #1234", "Uber ride"]
    assert df["amount"].tolist() == [499.0, 1250.5, 300.0]
    assert len(rep.issues) == 3


def test_strict_and_lenient_parsing():
    good = '{"results":[{"id":"T1","category":"Food","confidence":0.9,"explanation":"x","needs_review":false}]}'
    assert parse_strict(good, ["T1"])["T1"].category == "Food"
    assert parse_strict("```json\n" + good + "\n```", ["T1"]) is not None
    assert parse_strict('{"results":[{"id":"T1","category":"Snacks"}]}', ["T1"]) is None
    assert parse_lenient("T1: Transport\nT2: Nonsense", ["T1", "T2"]).keys() == {"T1"}


def test_grounding_check_catches_invented_numbers():
    facts = {"total": 1250.5, "pct": 12.3}
    assert assistant.grounding_check("You spent ₹1,250.50 (12.3%).", facts).grounded
    g = assistant.grounding_check("You spent ₹9,999 last month.", facts)
    assert not g.grounded and g.unsupported


def test_python_does_the_math():
    df = pd.DataFrame({"id": ["a", "b", "c"], "date": pd.to_datetime(["2026-09-01", "2026-10-01", "2026-10-02"]),
                       "description": ["x", "y", "z"], "amount": [100.0, 200.0, 50.0],
                       "category": ["Food", "Food", "Transport"], "month": ["2026-09", "2026-10", "2026-10"],
                       "merchant": ["X", "Y", "Z"]})
    r = assistant.execute_intent(df, QueryIntent(intent="total", category="Food", month="2026-10"))
    assert r["total"] == 200.0 and r["matching_transactions"] == 1
    r = assistant.execute_intent(df, QueryIntent(intent="compare_months", month="2026-10", month_b="2026-09"))
    assert r["difference"] == 150.0 and r["difference_pct"] == 150.0
    assert analytics.month_facts(df, "2026-10")["total_spent"] == 250.0


def test_end_to_end_offline():
    lab = pd.read_csv("data/labelled_transactions.csv")
    p = builtin_strategies(lab[lab.split == "dev"].to_dict("records"))["few_shot"]
    test = lab[lab.split == "test"].head(25)
    preds, st = categorise(test[["id", "description"]].to_dict("records"), p, make_llm("offline-simulator"))
    assert len(preds) == 25 and st.calls == 2 and st.strict_valid == 25


def test_dev_test_split_has_no_overlap():
    lab = pd.read_csv("data/labelled_transactions.csv")
    assert set(lab[lab.split == "dev"].id).isdisjoint(lab[lab.split == "test"].id)
    assert 0.65 < (lab.split == "dev").mean() < 0.75
