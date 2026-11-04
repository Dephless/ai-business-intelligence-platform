from app.schemas.analysis import Metric
from app.services.recommendation_engine import generate_recommendations


def test_detects_outlier():
    records = [{"revenue": value} for value in [100, 110, 105, 115, 108, 900]]

    metric = Metric(
        field="revenue",
        count=6,
        total=1438,
        average=1438 / 6,
        minimum=100,
        maximum=900,
    )

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 1
    assert recommendations[0].priority == "medium"
    assert "revenue" in recommendations[0].title


def test_detects_negative_values():
    records = [{"profit": value} for value in [-20, -10, 0, 10, 20, 30]]

    metric = Metric(
        field="profit",
        count=6,
        total=30,
        average=5,
        minimum=-20,
        maximum=30,
    )

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 1
    assert recommendations[0].priority == "high"
    assert "profit" in recommendations[0].title


def test_uses_fallback_when_no_anomaly_exists():
    records = [{"revenue": value} for value in [80, 90, 100, 110, 120]]

    metric = Metric(
        field="revenue",
        count=5,
        total=500,
        average=100,
        minimum=80,
        maximum=120,
    )

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 1
    assert recommendations[0].priority == "low"


def test_detects_multiple_conditions():
    records = [{"profit": value} for value in [-20, 0, 10, 20, 30, 900]]

    metric = Metric(
        field="profit",
        count=6,
        total=940,
        average=940 / 6,
        minimum=-20,
        maximum=900,
    )

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 2
    assert {item.priority for item in recommendations} == {"medium", "high"}


def test_uses_fallback_for_empty_metrics():
    recommendations = generate_recommendations([], [])

    assert len(recommendations) == 1
    assert recommendations[0].priority == "low"


def test_does_not_detect_iqr_outliers_with_fewer_than_four_values():
    records = [
        {"revenue": 100},
        {"revenue": 110},
        {"revenue": 120},
    ]

    metric = Metric(
        field="revenue",
        count=3,
        total=330,
        average=110,
        minimum=100,
        maximum=120,
    )

    recommendations = generate_recommendations([metric], records)

    assert len(recommendations) == 1
    assert recommendations[0].priority == "low"
    assert "business-specific" in recommendations[0].title.lower()
