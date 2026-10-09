from analytics_platform.datasets.gold import (
    build_forecasts_vs_facts_gold,
)


df = build_forecasts_vs_facts_gold()

columns = [
    "forecast_id",
    "topic",
    "forecast_operator",
    "forecast_value",
    "forecast_lower",
    "forecast_upper",
    "actual_value",
    "absolute_error",
    "percentage_error",
    "direction",
    "outcome_classification",
]

print(
    df[columns]
    .to_string(index=False)
)

print("\nShape:", df.shape)

print("\nClassification counts:")
print(
    df["outcome_classification"]
    .value_counts()
)

import pandas as pd
from analytics_platform.analytics.forecasts_vs_facts import (
    build_forecast_comparisons,
)

range_test = pd.DataFrame([
    {
        "forecast_id": "TEST_RANGE_1",
        "forecast_operator": "range",
        "forecast_value": None,
        "forecast_lower": 3.0,
        "forecast_upper": 4.0,
        "actual_value": 3.6,
    },
    {
        "forecast_id": "TEST_RANGE_2",
        "forecast_operator": "range",
        "forecast_value": None,
        "forecast_lower": 3.0,
        "forecast_upper": 4.0,
        "actual_value": 4.8,
    },
    {
        "forecast_id": "TEST_RANGE_3",
        "forecast_operator": "range",
        "forecast_value": None,
        "forecast_lower": 3.0,
        "forecast_upper": 4.0,
        "actual_value": 2.4,
    },
])

range_result = build_forecast_comparisons(range_test)

print("\nRange tests:")
print(
    range_result[
        [
            "forecast_id",
            "forecast_lower",
            "forecast_upper",
            "actual_value",
            "direction",
            "outcome_classification",
        ]
    ].to_string(index=False)
)
