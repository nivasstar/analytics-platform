import pandas as pd


def build_market_risk_snapshot(
    market_df: pd.DataFrame,
    spread_df: pd.DataFrame,
    unemployment_df: pd.DataFrame
) -> pd.DataFrame:

    latest_market = (
        market_df
        .sort_values("date")
        .iloc[-1]
    )

    latest_spread = (
        spread_df
        .sort_values("date")
        .iloc[-1]
    )

    latest_unemployment = (
        unemployment_df
        .sort_values("date")
        .iloc[-1]
    )

    snapshot = {
        "as_of_date": latest_market["date"],
        "spy_close": latest_market["close"],
        "ma_200": latest_market["ma_200"],
        "volatility_30d": latest_market["volatility_30d"],
        "drawdown": latest_market["drawdown"],
        "yield_spread_10y_3m": latest_spread["yield_spread_10y_3m"],
        "unemployment_rate": latest_unemployment["value"],
        "market_data_date": latest_market["date"],
        "yield_data_date": latest_spread["date"],
        "unemployment_data_date": latest_unemployment["date"],
    }

    return pd.DataFrame([snapshot])
