import pandas as pd


def calculate_yield_spread(
    yield_10y: pd.DataFrame,
    yield_3m: pd.DataFrame
) -> pd.DataFrame:

    ten_year = yield_10y[
        ["date", "value"]
    ].copy()

    three_month = yield_3m[
        ["date", "value"]
    ].copy()

    ten_year = ten_year.rename(
        columns={"value": "yield_10y"}
    )

    three_month = three_month.rename(
        columns={"value": "yield_3m"}
    )

    result = pd.merge(
        ten_year,
        three_month,
        on="date",
        how="inner"
    )

    result["yield_spread_10y_3m"] = (
        result["yield_10y"]
        - result["yield_3m"]
    )

    return result.sort_values(
        "date"
    ).reset_index(drop=True)
