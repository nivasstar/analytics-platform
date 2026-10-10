import pandas as pd
import yfinance as yf

from analytics_platform.ingestion.base import DataSource


class YahooSource(DataSource):

    def fetch(
        self,
        ticker=None,
        symbol=None,
        start=None,
        end=None,
        start_date=None,
        end_date=None,
        **kwargs,
    ):
        # Support either registry convention:
        # ticker: SPY
        # or
        # symbol: SPY
        resolved_ticker = ticker or symbol

        if not resolved_ticker:
            raise ValueError(
                "Yahoo source requires 'ticker' or 'symbol'"
            )

        # Support either date naming convention
        resolved_start = start or start_date
        resolved_end = end or end_date

        df = yf.download(
            resolved_ticker,
            start=resolved_start,
            end=resolved_end,
            progress=False,
            auto_adjust=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # yfinance often returns MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                col[0] if isinstance(col, tuple) else col
                for col in df.columns
            ]

        df = df.reset_index()

        df.columns = [
            str(col)
            .strip()
            .lower()
            .replace(" ", "_")
            for col in df.columns
        ]

        expected = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
        ]

        for column in expected:
            if column not in df.columns:
                df[column] = pd.NA

        # Remove incomplete Yahoo rows before validation.
        # Rows without a date or closing price cannot be used
        # for returns, averages, volatility, or drawdown.
        df = df[
            df["date"].notna()
            & df["close"].notna()
        ].copy()

        df = df.sort_values(
            "date"
        ).reset_index(
            drop=True
        )

        return df[expected]
