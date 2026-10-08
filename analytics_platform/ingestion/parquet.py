import os
from pathlib import Path

import pandas as pd

from analytics_platform.ingestion.base import DataSource


class ParquetSource(DataSource):

    def fetch(
        self,
        path,
        filters=None,
        **kwargs
    ):
        expanded_path = os.path.expandvars(
            os.path.expanduser(path)
        )

        parquet_path = Path(expanded_path)

        if not parquet_path.exists():
            raise FileNotFoundError(
                f"Parquet source not found: {parquet_path}"
            )

        df = pd.read_parquet(parquet_path)

        if filters:
            for column, value in filters.items():
                if column not in df.columns:
                    raise ValueError(
                        f"Filter column '{column}' "
                        f"not found in {parquet_path}"
                    )

                df = df[df[column] == value]

        return df.reset_index(drop=True)
