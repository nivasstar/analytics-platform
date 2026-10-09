from analytics_platform.datasets.gold import (
    build_forecasts_vs_facts_gold,
)


df = build_forecasts_vs_facts_gold()

columns = [
    "forecast_id",
    "topic",
    "forecast_value",
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
