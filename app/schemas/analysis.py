from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AnalysisCreate(BaseModel):
    dataset_name: str = Field(min_length=1, max_length=120)
    records: list[dict[str, Any]] = Field(min_length=1, max_length=5000)


class Metric(BaseModel):
    field: str
    count: int
    total: float
    average: float
    minimum: float
    maximum: float


class Recommendation(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    rationale: str
    confidence: float = Field(ge=0, le=1)


class AnalysisResult(BaseModel):
    summary: str
    record_count: int
    numeric_metrics: list[Metric]
    recommendations: list[Recommendation]
    llm_enhanced: bool = False


class AnalysisRead(BaseModel):
    id: int
    dataset_name: str
    record_count: int
    result: AnalysisResult
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
