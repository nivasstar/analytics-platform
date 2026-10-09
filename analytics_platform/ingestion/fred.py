import os
from fredapi import Fred

from analytics_platform.ingestion.base import DataSource


class FredSource(DataSource):

    def __init__(self):
        api_key = os.getenv("FRED_API_KEY", "").strip()

        if not api_key:
            raise ValueError(
                "FRED_API_KEY environment variable is not set"
            )

        self.client = Fred(api_key=api_key)

    def fetch(
        self,
        series_id,
        start_date=None,
        end_date=None,
        **kwargs
    ):
        series = self.client.get_series(
            series_id,
            observation_start=start_date,
            observation_end=end_date
        )

        if series.empty:
            raise ValueError(
                f"No FRED data returned for {series_id}"
            )

        df = series.reset_index()
        df.columns = ["date", "value"]

        return df
