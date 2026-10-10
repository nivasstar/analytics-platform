from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from analytics_platform.datasets.gold import (
    build_market_gold,
)

from analytics_platform.datasets.manager import (
    get_dataset,
)


ASSET_DIR = Path("reports/output/assets")
ASSET_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GENERIC CHART SUPPORT
# ============================================================

def render_line_chart(
    dataframe,
    x,
    y,
    title,
    output_path,
):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = dataframe.copy()

    if x not in df.columns:
        raise ValueError(
            f"Chart x column not found: {x}"
        )

    if y not in df.columns:
        raise ValueError(
            f"Chart y column not found: {y}"
        )

    if not pd.api.types.is_numeric_dtype(
        df[x]
    ):
        converted = pd.to_datetime(
            df[x],
            errors="coerce",
        )

        if converted.notna().any():
            df[x] = converted

    df[y] = pd.to_numeric(
        df[y],
        errors="coerce",
    )

    df = df.dropna(
        subset=[x, y]
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        df[x],
        df[y],
    )

    plt.title(title)
    plt.xlabel(
        x.replace("_", " ").title()
    )
    plt.ylabel(
        y.replace("_", " ").title()
    )

    plt.grid(alpha=0.25)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    return output_path


# ============================================================
# SHARED SAVE HELPER
# ============================================================

def _save_chart(filename):
    path = ASSET_DIR / filename

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    return f"assets/{filename}"


# ============================================================
# MARKET RISK
# ============================================================

def plot_spy_vs_ma200():
    df = build_market_gold(
        start_date="2024-01-01"
    ).copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["close"] = pd.to_numeric(
        df["close"],
        errors="coerce",
    )

    if "ma_200" in df.columns:
        df["ma_200"] = pd.to_numeric(
            df["ma_200"],
            errors="coerce",
        )

    df = df.dropna(
        subset=[
            "date",
            "close",
        ]
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        df["date"],
        df["close"],
        label="SPY Close",
    )

    if (
        "ma_200" in df.columns
        and df["ma_200"].notna().any()
    ):
        plt.plot(
            df["date"],
            df["ma_200"],
            label="200-Day Moving Average",
        )

    plt.title(
        "SPY Price vs 200-Day Moving Average"
    )

    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend()
    plt.grid(alpha=0.25)

    return _save_chart(
        "spy_vs_ma200.png"
    )


def plot_yield_spread_vs_unemployment():
    yield_10y = get_dataset(
        "macro.yield_10y"
    ).copy()

    yield_3m = get_dataset(
        "macro.yield_3m"
    ).copy()

    unemployment = get_dataset(
        "macro.unemployment"
    ).copy()

    for df in [
        yield_10y,
        yield_3m,
        unemployment,
    ]:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
        )

        df["value"] = pd.to_numeric(
            df["value"],
            errors="coerce",
        )

    yield_10y = yield_10y.rename(
        columns={
            "value": "yield_10y",
        }
    )

    yield_3m = yield_3m.rename(
        columns={
            "value": "yield_3m",
        }
    )

    unemployment = unemployment.rename(
        columns={
            "value": "unemployment_rate",
        }
    )

    yield_10y["month"] = (
        yield_10y["date"]
        .dt.to_period("M")
    )

    yield_3m["month"] = (
        yield_3m["date"]
        .dt.to_period("M")
    )

    unemployment["month"] = (
        unemployment["date"]
        .dt.to_period("M")
    )

    y10 = (
        yield_10y
        .dropna(
            subset=["yield_10y"]
        )
        .groupby("month")[
            "yield_10y"
        ]
        .last()
        .reset_index()
    )

    y3 = (
        yield_3m
        .dropna(
            subset=["yield_3m"]
        )
        .groupby("month")[
            "yield_3m"
        ]
        .last()
        .reset_index()
    )

    unemp = (
        unemployment
        .dropna(
            subset=["unemployment_rate"]
        )
        .groupby("month")[
            "unemployment_rate"
        ]
        .last()
        .reset_index()
    )

    macro = (
        y10
        .merge(
            y3,
            on="month",
            how="inner",
        )
        .merge(
            unemp,
            on="month",
            how="inner",
        )
    )

    macro["yield_spread"] = (
        macro["yield_10y"]
        - macro["yield_3m"]
    )

    macro["date"] = (
        macro["month"]
        .dt.to_timestamp()
    )

    macro = macro.tail(60)

    plt.figure(figsize=(10, 5))

    plt.plot(
        macro["date"],
        macro["yield_spread"],
        label="10Y-3M Yield Spread",
    )

    plt.plot(
        macro["date"],
        macro["unemployment_rate"],
        label="Unemployment Rate",
    )

    plt.axhline(
        0,
        linewidth=1,
    )

    plt.title(
        "Yield Curve Spread vs Unemployment"
    )

    plt.xlabel("Date")
    plt.ylabel("Percent")

    plt.legend()
    plt.grid(alpha=0.25)

    return _save_chart(
        "yield_spread_unemployment.png"
    )


def build_market_risk_charts():
    return {
        "spy_ma200": (
            plot_spy_vs_ma200()
        ),
        "macro": (
            plot_yield_spread_vs_unemployment()
        ),
    }


# ============================================================
# ECONOMIC HISTORY
# ============================================================

def plot_population_history(
    df,
    country,
):
    data = df.copy()

    data["year"] = pd.to_numeric(
        data["year"],
        errors="coerce",
    )

    data["population"] = pd.to_numeric(
        data["population"],
        errors="coerce",
    )

    data = (
        data
        .dropna(
            subset=[
                "year",
                "population",
            ]
        )
        .sort_values("year")
    )

    if data.empty:
        return None

    plt.figure(figsize=(10, 5))

    plt.plot(
        data["year"],
        data["population"],
    )

    plt.title(
        f"{country} Population Through History"
    )

    plt.xlabel("Year")
    plt.ylabel("Population")

    plt.grid(alpha=0.25)

    return _save_chart(
        "economic_history_population.png"
    )


def plot_gdp_per_capita_history(
    df,
    country,
):
    data = df.copy()

    data["year"] = pd.to_numeric(
        data["year"],
        errors="coerce",
    )

    data["gdp_per_capita"] = pd.to_numeric(
        data["gdp_per_capita"],
        errors="coerce",
    )

    data = (
        data
        .dropna(
            subset=[
                "year",
                "gdp_per_capita",
            ]
        )
        .sort_values("year")
    )

    if data.empty:
        return None

    plt.figure(figsize=(10, 5))

    plt.plot(
        data["year"],
        data["gdp_per_capita"],
    )

    plt.title(
        f"{country} GDP per Capita Through History"
    )

    plt.xlabel("Year")
    plt.ylabel("GDP per Capita")

    plt.grid(alpha=0.25)

    return _save_chart(
        "economic_history_gdp_per_capita.png"
    )


def build_economic_history_charts(
    df,
    country,
):
    return {
        "population": (
            plot_population_history(
                df,
                country,
            )
        ),
        "gdp_per_capita": (
            plot_gdp_per_capita_history(
                df,
                country,
            )
        ),
    }


# ============================================================
# FORECASTS VS FACTS
# ============================================================

def _point_forecasts(df):
    point = df[
        (df["forecast_operator"] == "eq")
        & df["forecast_value"].notna()
        & df["actual_value"].notna()
    ].copy()

    point["forecast_value"] = (
        pd.to_numeric(
            point["forecast_value"],
            errors="coerce",
        )
    )

    point["actual_value"] = (
        pd.to_numeric(
            point["actual_value"],
            errors="coerce",
        )
    )

    point = point.dropna(
        subset=[
            "forecast_value",
            "actual_value",
        ]
    )

    if "percentage_error" in point.columns:
        point["abs_percentage_error"] = (
            pd.to_numeric(
                point["percentage_error"],
                errors="coerce",
            ).abs()
        )

    return point


def plot_forecast_vs_actual(df):
    point = _point_forecasts(df)

    if point.empty:
        return None

    plt.figure(figsize=(7, 7))

    plt.scatter(
        point["forecast_value"],
        point["actual_value"],
        s=60,
    )

    minimum = min(
        point["forecast_value"].min(),
        point["actual_value"].min(),
    )

    maximum = max(
        point["forecast_value"].max(),
        point["actual_value"].max(),
    )

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--",
        label="Perfect Forecast",
    )

    plt.title(
        "Forecast vs Actual Outcomes"
    )

    plt.xlabel("Forecast")
    plt.ylabel("Actual")

    plt.legend()
    plt.grid(alpha=0.25)

    return _save_chart(
        "forecast_vs_actual_scatter.png"
    )


def plot_error_by_case(df):
    point = _point_forecasts(df)

    if "abs_percentage_error" not in point.columns:
        return None

    point = point.dropna(
        subset=[
            "abs_percentage_error",
        ]
    )

    if point.empty:
        return None

    largest = (
        point
        .nlargest(
            15,
            "abs_percentage_error",
        )
        .sort_values(
            "abs_percentage_error"
        )
    )

    labels = (
        largest["topic"]
        .astype(str)
        .str.slice(0, 45)
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        labels,
        largest[
            "abs_percentage_error"
        ],
    )

    plt.title(
        "Largest Forecast Errors"
    )

    plt.xlabel(
        "Absolute Percentage Error (%)"
    )

    plt.ylabel("Forecast Case")

    plt.grid(
        axis="x",
        alpha=0.25,
    )

    return _save_chart(
        "error_by_case.png"
    )


def plot_accuracy_by_horizon(df):
    point = _point_forecasts(df)

    if "abs_percentage_error" not in point.columns:
        return None

    point = point.dropna(
        subset=[
            "forecast_horizon_years",
            "abs_percentage_error",
        ]
    )

    if point.empty:
        return None

    def bucket(years):
        if years < 1:
            return "< 1 year"

        if years < 3:
            return "1-3 years"

        if years < 10:
            return "3-10 years"

        return "10+ years"

    point["horizon_bucket"] = (
        point[
            "forecast_horizon_years"
        ]
        .apply(bucket)
    )

    order = [
        "< 1 year",
        "1-3 years",
        "3-10 years",
        "10+ years",
    ]

    summary = (
        point
        .groupby(
            "horizon_bucket"
        )[
            "abs_percentage_error"
        ]
        .mean()
        .reindex(order)
        .dropna()
    )

    if summary.empty:
        return None

    plt.figure(figsize=(8, 5))

    plt.bar(
        summary.index,
        summary.values,
    )

    plt.title(
        "Average Forecast Error by Horizon"
    )

    plt.xlabel(
        "Forecast Horizon"
    )

    plt.ylabel(
        "Mean Absolute Percentage Error (%)"
    )

    plt.grid(
        axis="y",
        alpha=0.25,
    )

    return _save_chart(
        "accuracy_by_horizon.png"
    )


def build_forecasts_vs_facts_charts(df):
    return {
        "scatter": (
            plot_forecast_vs_actual(df)
        ),
        "errors": (
            plot_error_by_case(df)
        ),
        "horizon": (
            plot_accuracy_by_horizon(df)
        ),
    }


# ============================================================
# DECISIONS VS OUTCOMES
# ============================================================

def _decision_prediction_value(row):
    operator = row.get(
        "predicted_operator"
    )

    value = pd.to_numeric(
        row.get("predicted_value"),
        errors="coerce",
    )

    lower = pd.to_numeric(
        row.get("predicted_lower"),
        errors="coerce",
    )

    upper = pd.to_numeric(
        row.get("predicted_upper"),
        errors="coerce",
    )

    if operator == "range":
        if (
            pd.notna(lower)
            and pd.notna(upper)
        ):
            return (
                lower + upper
            ) / 2

    return value


def plot_decision_prediction_vs_outcome(
    df,
):
    data = df.copy()

    data[
        "prediction_chart_value"
    ] = data.apply(
        _decision_prediction_value,
        axis=1,
    )

    data["outcome_value"] = (
        pd.to_numeric(
            data["outcome_value"],
            errors="coerce",
        )
    )

    data = data.dropna(
        subset=[
            "prediction_chart_value",
            "outcome_value",
        ]
    )

    if data.empty:
        return None

    chart_data = []

    for _, row in data.iterrows():
        chart_data.append(
            {
                "label": str(
                    row["decision"]
                )[:40],
                "series": "Prediction",
                "value": row[
                    "prediction_chart_value"
                ],
            }
        )

        chart_data.append(
            {
                "label": str(
                    row["decision"]
                )[:40],
                "series": "Observed",
                "value": row[
                    "outcome_value"
                ],
            }
        )

    chart_df = pd.DataFrame(
        chart_data
    )

    pivot = chart_df.pivot(
        index="label",
        columns="series",
        values="value",
    )

    plt.figure(figsize=(10, 6))

    pivot.plot(
        kind="bar",
        ax=plt.gca(),
    )

    plt.title(
        "Published Expectation vs Observed Outcome"
    )

    plt.xlabel("Decision")
    plt.ylabel("Comparable Metric")

    plt.xticks(
        rotation=20,
        ha="right",
    )

    plt.legend()
    plt.grid(
        axis="y",
        alpha=0.25,
    )

    return _save_chart(
        "decisions_prediction_vs_outcome.png"
    )


def plot_decision_horizons(df):
    data = df.copy()

    data["outcome_horizon_years"] = (
        pd.to_numeric(
            data["outcome_horizon_years"],
            errors="coerce",
        )
    )

    data = (
        data
        .dropna(
            subset=[
                "outcome_horizon_years",
            ]
        )
        .sort_values(
            "outcome_horizon_years"
        )
    )

    if data.empty:
        return None

    labels = (
        data["decision"]
        .astype(str)
        .str.slice(0, 45)
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        labels,
        data[
            "outcome_horizon_years"
        ],
    )

    plt.title(
        "Time from Decision to Observed Outcome"
    )

    plt.xlabel("Years")
    plt.ylabel("Decision")

    plt.grid(
        axis="x",
        alpha=0.25,
    )

    return _save_chart(
        "decisions_outcome_horizon.png"
    )


def build_decisions_vs_outcomes_charts(
    df,
):
    return {
        "comparison": (
            plot_decision_prediction_vs_outcome(
                df
            )
        ),
        "horizon": (
            plot_decision_horizons(
                df
            )
        ),
    }
