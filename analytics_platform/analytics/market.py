import pandas as pd


def add_market_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "close" not in result.columns:
        raise ValueError("Expected 'close' column")

    result = result.sort_values("date").reset_index(drop=True)

    result["ma_200"] = (
        result["close"]
        .rolling(window=200, min_periods=1)
        .mean()
    )

    result["daily_return"] = (
        result["close"]
        .pct_change()
    )

    result["volatility_30d"] = (
        result["daily_return"]
        .rolling(window=30, min_periods=2)
        .std()
        * (252 ** 0.5)
    )

    result["running_peak"] = (
        result["close"]
        .cummax()
    )

    result["drawdown"] = (
        result["close"] / result["running_peak"] - 1
    )

    return result
