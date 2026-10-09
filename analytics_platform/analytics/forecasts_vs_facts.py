import pandas as pd


def build_forecast_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    # ---------------------------------------------------------
    # 1. Normalize date columns FIRST
    # ---------------------------------------------------------
    for column in [
        "forecast_date",
        "target_date",
        "actual_date",
    ]:
        if column in result.columns:
            result[column] = pd.to_datetime(
                result[column],
                errors="coerce"
            )

    # ---------------------------------------------------------
    # 2. Forecast horizon
    # ---------------------------------------------------------
    if (
        "forecast_date" in result.columns
        and "target_date" in result.columns
    ):
        result["forecast_horizon_days"] = (
            result["target_date"]
            - result["forecast_date"]
        ).dt.days

        result["forecast_horizon_years"] = (
            result["forecast_horizon_days"] / 365.25
        ).round(1)

        def horizon_label(days):
            if pd.isna(days):
                return "unknown"

            if days < 60:
                return f"{int(round(days))} days"

            if days < 730:
                months = round(days / 30.44)
                return f"{months} months"

            years = round(days / 365.25, 1)
            return f"{years} years"

        result["forecast_horizon"] = (
            result["forecast_horizon_days"]
            .apply(horizon_label)
        )

    else:
        result["forecast_horizon_days"] = pd.NA
        result["forecast_horizon_years"] = pd.NA
        result["forecast_horizon"] = "unknown"

    # ---------------------------------------------------------
    # 3. Normalize numeric columns
    # ---------------------------------------------------------
    numeric_columns = [
        "forecast_value",
        "forecast_lower",
        "forecast_upper",
        "actual_value",
    ]

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="coerce"
            )

    # ---------------------------------------------------------
    # 4. Point-forecast error calculations
    # ---------------------------------------------------------
    result["absolute_error"] = (
        result["actual_value"]
        - result["forecast_value"]
    )

    result["percentage_error"] = (
        result["absolute_error"]
        / result["forecast_value"].abs()
        * 100
    )

    # ---------------------------------------------------------
    # 5. Classification
    # ---------------------------------------------------------
    def classify(row):
        operator = row.get(
            "forecast_operator",
            "eq"
        )

        actual = row.get("actual_value")
        forecast = row.get("forecast_value")

        lower = row.get("forecast_lower")
        upper = row.get("forecast_upper")

        if pd.isna(actual):
            return "insufficient_data"

        if operator == "eq":
            if pd.isna(forecast):
                return "insufficient_data"

            pct_error = abs(
                row["percentage_error"]
            )

            if pct_error <= 5:
                return "very_close"

            if pct_error <= 15:
                return "close"

            if actual > forecast:
                return "actual_above_forecast"

            return "actual_below_forecast"

        if operator == "gt":
            if pd.isna(forecast):
                return "insufficient_data"

            return (
                "threshold_met"
                if actual > forecast
                else "threshold_missed"
            )

        if operator == "lt":
            if pd.isna(forecast):
                return "insufficient_data"

            return (
                "threshold_met"
                if actual < forecast
                else "threshold_missed"
            )

        if operator == "range":
            if pd.isna(lower) or pd.isna(upper):
                return "insufficient_data"

            if lower <= actual <= upper:
                return "within_range"

            if actual < lower:
                return "below_range"

            return "above_range"

        return "unknown_operator"

    result["outcome_classification"] = (
        result.apply(
            classify,
            axis=1
        )
    )

    # ---------------------------------------------------------
    # 6. Direction
    # ---------------------------------------------------------
    def direction(row):
        operator = row.get(
            "forecast_operator",
            "eq"
        )

        actual = row.get("actual_value")
        forecast = row.get("forecast_value")

        if pd.isna(actual):
            return "unknown"

        if operator == "range":
            lower = row.get("forecast_lower")
            upper = row.get("forecast_upper")

            if pd.isna(lower) or pd.isna(upper):
                return "unknown"

            if actual < lower:
                return "below"

            if actual > upper:
                return "above"

            return "within"

        if pd.isna(forecast):
            return "unknown"

        if actual > forecast:
            return "above"

        if actual < forecast:
            return "below"

        return "equal"

    result["direction"] = (
        result.apply(
            direction,
            axis=1
        )
    )

    return result
