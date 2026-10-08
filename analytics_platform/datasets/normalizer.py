from datetime import datetime, timezone

import pandas as pd


class DatasetNormalizer:

    @staticmethod
    def normalize(
        df: pd.DataFrame,
        dataset_name: str,
        source_type: str
    ) -> pd.DataFrame:

        result = df.copy()

        # Standardize columns
        result.columns = [
            str(col)
            .strip()
            .lower()
            .replace(" ", "_")
            for col in result.columns
        ]

        # Standardize date
        if "date" in result.columns:
            result["date"] = pd.to_datetime(
                result["date"],
                errors="coerce"
            )

        # Add lineage metadata
        result["dataset_id"] = dataset_name
        result["source"] = source_type

        result["loaded_at"] = datetime.now(
            timezone.utc
        )

        return result
