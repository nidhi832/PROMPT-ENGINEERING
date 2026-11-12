"""Pydantic schemas: every LLM output is validated against one of these before it is shown."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]
Category = Literal["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]


class CategoryResult(BaseModel):
    id: str
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = Field(min_length=1, max_length=300)
    needs_review: bool


class BatchCategorization(BaseModel):
    results: list[CategoryResult]


class QueryIntent(BaseModel):
    intent: Literal["total", "by_category", "top_categories", "compare_months",
                    "largest", "count", "average", "list", "unsupported"]
    category: Optional[Category] = None
    month: Optional[str] = Field(default=None, description="YYYY-MM")
    month_b: Optional[str] = Field(default=None, description="second month for comparisons, YYYY-MM")
    n: int = Field(default=5, ge=1, le=20)

    @field_validator("month", "month_b")
    @classmethod
    def _month_fmt(cls, v):
        if v is None:
            return v
        if len(v) != 7 or v[4] != "-":
            raise ValueError("month must be YYYY-MM")
        return v


class Suggestion(BaseModel):
    title: str
    detail: str
    category: Optional[Category] = None
    estimated_monthly_saving: Optional[float] = Field(default=None, ge=0)


class BudgetAdvice(BaseModel):
    summary: str
    suggestions: list[Suggestion] = Field(max_length=3)
    missing_information: list[str] = []


class MonthlyReport(BaseModel):
    headline: str
    observations: list[str] = Field(min_length=1, max_length=6)
    next_steps: list[str] = Field(min_length=1, max_length=4)
