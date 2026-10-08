from pathlib import Path

import pandas as pd


class StorageManager:

    @staticmethod
    def write_parquet(df: pd.DataFrame, path: str):
        output_path = Path(path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        df.to_parquet(
            output_path,
            index=False
        )

        return output_path

    @staticmethod
    def read_parquet(path: str):
        input_path = Path(path)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {input_path}"
            )

        return pd.read_parquet(input_path)

    @staticmethod
    def exists(path: str):
        return Path(path).exists()
