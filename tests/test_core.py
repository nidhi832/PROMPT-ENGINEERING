import io

import pandas as pd
import pytest
from pydantic import ValidationError

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


def test_import_rejects_infinite_and_sub_cent_amounts():
    csv = io.BytesIO(b"date,description,amount\n2026-10-01,A,inf\n2026-10-01,B,-inf\n"
                     b"2026-10-01,C,0.001\n2026-10-01,D,-12.50\n")
    df, rep = load_transactions(csv)
    assert df["amount"].tolist() == [12.50]
    assert [issue["row"] for issue in rep.issues] == [2, 3, 4]
    assert "negative" in rep.notes[0]


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


@pytest.mark.parametrize("month", ["abcd-ef", "2026-00", "2026-13", "0000-01"])
def test_query_intent_rejects_invalid_months(month):
    with pytest.raises(ValidationError):
        QueryIntent(intent="total", month=month)


def test_offline_comparison_respects_month_order_and_reports_missing_data():
    df, _ = load_transactions(io.BytesIO(CSV))
    df["category"] = "Food"
    llm = make_llm("offline-simulator")
    answer = assistant.ask(df, "Compare October versus September", llm)
    assert answer.result["month"] == "October 2026"
    assert answer.result["difference"] == 1051.5
    for question in ("Compare September", "Compare 2025-12 versus 2026-10"):
        answer = assistant.ask(df, question, llm)
        assert answer.text == answer.result["comparison_unavailable"]


def test_category_comparison_omits_percent_when_previous_spend_is_zero():
    df, _ = load_transactions(io.BytesIO(CSV))
    df["category"] = ["Entertainment", "Food", "Food"]
    answer = assistant.ask(df, "Compare Food in October versus September", make_llm("offline-simulator"))
    assert answer.result["difference_pct"] is None
    assert "%" not in answer.text


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
