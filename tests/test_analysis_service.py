import json
from types import SimpleNamespace

import pytest

from app.schemas.analysis import Metric
from app.services import analysis_service
from app.services.recommendation_engine import generate_recommendations


def test_numeric_metrics_calculates_statistics():
    records = [
        {"revenue": 100, "cost": 40, "active": True},
        {"revenue": 200, "cost": 60, "active": False},
        {"revenue": 300, "cost": 80, "active": True},
    ]

    metrics = analysis_service._numeric_metrics(records)

    assert [metric.field for metric in metrics] == ["cost", "revenue"]

    revenue = next(metric for metric in metrics if metric.field == "revenue")
    assert revenue.count == 3
    assert revenue.total == 600
    assert revenue.average == 200
    assert revenue.minimum == 100
    assert revenue.maximum == 300

    cost = next(metric for metric in metrics if metric.field == "cost")
    assert cost.count == 3
    assert cost.total == 180
    assert cost.average == 60


def test_numeric_metrics_ignores_booleans_and_non_numeric_values():
    records = [
        {"active": True, "name": "North"},
        {"active": False, "name": "South"},
    ]

    assert analysis_service._numeric_metrics(records) == []


def test_numeric_metrics_handles_empty_records():
    assert analysis_service._numeric_metrics([]) == []


def test_baseline_recommendations_detects_outlier():
    metric = Metric(
        field="revenue",
        count=3,
        total=600,
        average=200,
        minimum=100,
        maximum=500,
    )
    records = [{"revenue": value} for value in [100, 110, 105, 115, 108, 900]]

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 1
    assert recommendations[0].title == "Investigate statistical outliers in revenue"
    assert recommendations[0].priority == "medium"


def test_baseline_recommendations_detects_negative_values():
    metric = Metric(
        field="profit",
        count=3,
        total=10,
        average=10 / 3,
        minimum=-20,
        maximum=30,
    )

    records = [{"profit": value} for value in [-20, -10, 0, 10, 20, 30]]

    recommendations = generate_recommendations([metric], records)

    assert any(
        recommendation.title == "Review negative values in profit"
        and recommendation.priority == "high"
        for recommendation in recommendations
    )


def test_baseline_recommendations_uses_fallback():
    metric = Metric(
        field="revenue",
        count=3,
        total=300,
        average=100,
        minimum=80,
        maximum=120,
    )
    records = [{"revenue": value} for value in [80, 90, 100, 110, 120]]

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 1
    assert recommendations[0].priority == "low"
    assert recommendations[0].title == ("Define business-specific performance thresholds")


@pytest.mark.parametrize(
    ("enable_llm", "api_key"),
    [
        (False, "test-key"),
        (True, None),
    ],
)
def test_llm_recommendations_returns_none_when_not_configured(
    monkeypatch,
    enable_llm,
    api_key,
):
    monkeypatch.setattr(analysis_service.settings, "enable_llm", enable_llm)
    monkeypatch.setattr(analysis_service.settings, "gemini_api_key", api_key)

    result = analysis_service._llm_recommendations("sales", [], [])

    assert result is None


def test_llm_recommendations_parses_response(monkeypatch):
    expected = {
        "summary": "Sales performance is stable.",
        "recommendations": [],
    }

    def fake_create(**kwargs):
        assert kwargs["model"] == analysis_service.settings.openai_model
        assert kwargs["response_format"] == {"type": "json_object"}
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(expected)))]
        )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )

    monkeypatch.setattr(analysis_service.settings, "enable_llm", True)
    monkeypatch.setattr(analysis_service.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        analysis_service,
        "OpenAI",
        lambda **kwargs: fake_client,
    )

    result = analysis_service._llm_recommendations(
        "sales",
        [{"revenue": 100}],
        [],
    )

    assert result == expected


def test_llm_recommendations_rejects_empty_response(monkeypatch):
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
                )
            )
        )
    )

    monkeypatch.setattr(analysis_service.settings, "enable_llm", True)
    monkeypatch.setattr(analysis_service.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        analysis_service,
        "OpenAI",
        lambda **kwargs: fake_client,
    )

    with pytest.raises(ValueError, match="empty response"):
        analysis_service._llm_recommendations("sales", [], [])


def test_llm_recommendations_rejects_non_object_json(monkeypatch):
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[
                        SimpleNamespace(message=SimpleNamespace(content='["not", "an", "object"]'))
                    ]
                )
            )
        )
    )

    monkeypatch.setattr(analysis_service.settings, "enable_llm", True)
    monkeypatch.setattr(analysis_service.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        analysis_service,
        "OpenAI",
        lambda **kwargs: fake_client,
    )

    with pytest.raises(ValueError, match="JSON object"):
        analysis_service._llm_recommendations("sales", [], [])


def test_analyze_dataset_uses_baseline_when_llm_is_disabled(monkeypatch):
    monkeypatch.setattr(analysis_service.settings, "enable_llm", False)

    result = analysis_service.analyze_dataset(
        "sales",
        [{"revenue": 100}, {"revenue": 200}],
    )

    assert result.record_count == 2
    assert result.llm_enhanced is False
    assert result.numeric_metrics[0].field == "revenue"
    assert result.summary == ("Analyzed 2 records in 'sales'. Found 1 numeric fields.")


def test_analyze_dataset_uses_llm_recommendations(monkeypatch):
    llm_response = {
        "summary": "Revenue increased steadily.",
        "recommendations": [
            {
                "title": "Review regional performance",
                "description": "Compare revenue across regions.",
                "priority": "medium",
                "rationale": "Regional differences may reveal opportunities.",
                "confidence": 0.9,
            }
        ],
    }

    monkeypatch.setattr(
        analysis_service,
        "_llm_recommendations",
        lambda *args: llm_response,
    )

    result = analysis_service.analyze_dataset(
        "sales",
        [{"revenue": 100}, {"revenue": 200}],
    )

    assert result.llm_enhanced is True
    assert result.summary == "Revenue increased steadily."
    assert len(result.recommendations) == 1
    assert result.recommendations[0].title == "Review regional performance"


def test_analyze_dataset_rejects_invalid_llm_recommendations(monkeypatch):
    monkeypatch.setattr(
        analysis_service,
        "_llm_recommendations",
        lambda *args: {"recommendations": "invalid"},
    )

    with pytest.raises(ValueError, match="must be a list"):
        analysis_service.analyze_dataset("sales", [{"revenue": 100}])


def test_analyze_dataset_uses_default_summary_if_llm_summary_is_empty(monkeypatch):
    monkeypatch.setattr(
        analysis_service,
        "_llm_recommendations",
        lambda *args: {"summary": "  ", "recommendations": []},
    )

    result = analysis_service.analyze_dataset(
        "sales",
        [{"revenue": 100}],
    )

    assert result.llm_enhanced is True
    assert result.summary == ("Analyzed 1 records in 'sales'. Found 1 numeric fields.")
