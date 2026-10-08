import pandas as pd
import yfinance as yf

from analytics_platform.ingestion.base import DataSource


class YahooSource(DataSource):

    def fetch(
        self,
        symbol,
        start_date=None,
        end_date=None,
        **kwargs
    ):
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            raise ValueError(
                f"No Yahoo Finance data returned for {symbol}"
            )

        df = df.reset_index()

        # Flatten yfinance MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                col[0] if col[1] == "" else col[0]
                for col in df.columns
            ]

        # Standardize column names
        df.columns = [
            str(col).strip().lower().replace(" ", "_")
            for col in df.columns
        ]

        expected_columns = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
        ]

        available_columns = [
            col for col in expected_columns
            if col in df.columns
        ]

        return df[available_columns]
