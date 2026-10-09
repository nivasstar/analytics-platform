import pandas as pd


def build_forecast_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["forecast_value"] = pd.to_numeric(
        result["forecast_value"],
        errors="coerce"
    )

    result["actual_value"] = pd.to_numeric(
        result["actual_value"],
        errors="coerce"
    )

    result["absolute_error"] = (
        result["actual_value"]
        - result["forecast_value"]
    )

    result["percentage_error"] = (
        result["absolute_error"]
        / result["forecast_value"].abs()
        * 100
    )

    def classify(row):
        forecast = row["forecast_value"]
        actual = row["actual_value"]

        if pd.isna(forecast) or pd.isna(actual):
            return "insufficient_data"

        pct_error = abs(row["percentage_error"])

        if pct_error <= 5:
            return "very_close"

        if pct_error <= 15:
            return "close"

        if actual > forecast:
            return "actual_above_forecast"

        return "actual_below_forecast"

    result["outcome_classification"] = result.apply(
        classify,
        axis=1
    )

    result["direction"] = result["absolute_error"].apply(
        lambda x:
            "above"
            if x > 0
            else "below"
            if x < 0
            else "equal"
    )

    return result
