import math
import statistics
from typing import Any

from app.schemas.analysis import Metric, Recommendation


def generate_recommendations(
    metrics: list[Metric],
    records: list[dict[str, Any]],
) -> list[Recommendation]:
    """Generate deterministic recommendations from business data."""
    recommendations: list[Recommendation] = []

    for metric in metrics:
        values = [
            float(row[metric.field])
            for row in records
            if isinstance(row.get(metric.field), (int, float))
            and not isinstance(row.get(metric.field), bool)
            and math.isfinite(float(row[metric.field]))
        ]

        # Detect statistical outliers using the interquartile range.
        if len(values) >= 4:
            quartiles = statistics.quantiles(
                values,
                n=4,
                method="inclusive",
            )
            q1 = quartiles[0]
            q3 = quartiles[2]
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = [value for value in values if value < lower_bound or value > upper_bound]

            if outliers:
                recommendations.append(
                    Recommendation(
                        title=f"Investigate statistical outliers in {metric.field}",
                        description=(
                            f"Detected {len(outliers)} statistical outlier(s) "
                            f"outside the IQR bounds "
                            f"({lower_bound:.2f} to {upper_bound:.2f})."
                        ),
                        priority="medium",
                        rationale=(
                            "Values outside the 1.5 × IQR boundaries "
                            "may indicate unusual business activity "
                            "and should be investigated."
                        ),
                        confidence=0.85,
                    )
                )

        # Detect negative values that may require business review.
        if metric.minimum < 0:
            recommendations.append(
                Recommendation(
                    title=f"Review negative values in {metric.field}",
                    description=(
                        f"At least one negative value was found (minimum: {metric.minimum})."
                    ),
                    priority="high",
                    rationale=(
                        "Negative values may be valid, but should be checked "
                        "against the business meaning of this field."
                    ),
                    confidence=0.8,
                )
            )

    if not recommendations:
        recommendations.append(
            Recommendation(
                title="Define business-specific performance thresholds",
                description=("No obvious numeric anomaly was detected by the baseline rules."),
                priority="low",
                rationale=(
                    "Domain-specific thresholds make future recommendations "
                    "more relevant and measurable."
                ),
                confidence=0.65,
            )
        )

    return recommendations
