from pathlib import Path

import pandas as pd

from analytics_platform.ingestion.base import DataSource


class CSVSource(DataSource):

    def fetch(self, path, **kwargs):
        csv_path = Path(path)

        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSV source not found: {csv_path}"
            )

        return pd.read_csv(csv_path)
