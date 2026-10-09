from analytics_platform.analytics.market import add_market_metrics
from analytics_platform.datasets import get_dataset
from analytics_platform.datasets.storage import StorageManager
from analytics_platform.analytics.risk import build_market_risk_snapshot
from analytics_platform.analytics.forecasts_vs_facts import (
    build_forecast_comparisons,
)
from analytics_platform.analytics.economic_history import (
    build_country_timeline,
)

def build_market_gold(
    start_date="2025-01-01"
):
    df = get_dataset(
        "market.spy_prices",
        start_date=start_date
    )

    gold_df = add_market_metrics(df)

    path = "data/gold/market/spy_metrics.parquet"

    StorageManager.write_parquet(
        gold_df,
        path
    )

    return gold_df

from analytics_platform.analytics.macro import calculate_yield_spread


def build_macro_gold():

    yield_10y = get_dataset(
        "macro.yield_10y"
    )

    yield_3m = get_dataset(
        "macro.yield_3m"
    )

    unemployment = get_dataset(
        "macro.unemployment"
    )

    spread_df = calculate_yield_spread(
        yield_10y,
        yield_3m
    )

    StorageManager.write_parquet(
        spread_df,
        "data/gold/macro/yield_spread.parquet"
    )

    unemployment_path = (
        "data/gold/macro/unemployment.parquet"
    )

    StorageManager.write_parquet(
        unemployment,
        unemployment_path
    )

    return spread_df, unemployment


def build_risk_snapshot():

    market_df = build_market_gold()

    spread_df, unemployment_df = build_macro_gold()

    snapshot_df = build_market_risk_snapshot(
        market_df,
        spread_df,
        unemployment_df
    )

    StorageManager.write_parquet(
        snapshot_df,
        "data/gold/market_risk_snapshot.parquet"
    )

    return snapshot_df


def build_economic_history_gold(
    country="India"
):

    country_history = get_dataset(
        "economic_history.country_history"
    )

    long_population = get_dataset(
        "economic_history.long_population"
    )

    world_bank = get_dataset(
        "economic_history.world_bank_history"
    )

    timeline = build_country_timeline(
        country_history,
        long_population,
        world_bank,
        country
    )

    safe_country = (
        country
        .lower()
        .replace(" ", "_")
    )

    path = (
        "data/gold/economic_history/"
        f"{safe_country}_timeline.parquet"
    )

    StorageManager.write_parquet(
        timeline,
        path
    )

    return timeline

def build_forecasts_vs_facts_gold():

    source_df = get_dataset(
        "forecasts_vs_facts.seed"
    )

    gold_df = build_forecast_comparisons(
        source_df
    )

    StorageManager.write_parquet(
        gold_df,
        "data/gold/forecasts_vs_facts/comparisons.parquet"
    )

    return gold_df
