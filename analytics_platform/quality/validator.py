import pandas as pd


class DataQualityError(Exception):
    pass


class DatasetValidator:

    @staticmethod
    def validate(df: pd.DataFrame, rules: dict, dataset_name: str):
        errors = []

        if df.empty:
            errors.append("dataset is empty")

        required_columns = rules.get("required_columns", [])
        for column in required_columns:
            if column not in df.columns:
                errors.append(f"missing required column: {column}")

        for column in rules.get("not_null", []):
            if column in df.columns and df[column].isna().any():
                errors.append(f"null values found in: {column}")

        for column in rules.get("unique", []):
            if column in df.columns and df[column].duplicated().any():
                errors.append(f"duplicate values found in: {column}")

        for column in rules.get("numeric", []):
            if column in df.columns:
                converted = pd.to_numeric(df[column], errors="coerce")
                if converted.isna().sum() > df[column].isna().sum():
                    errors.append(f"non-numeric values found in: {column}")

        if errors:
            raise DataQualityError(
                f"Data quality failed for '{dataset_name}': "
                + "; ".join(errors)
            )

        return True
