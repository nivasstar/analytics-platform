from pathlib import Path

from analytics_platform.datasets import get_dataset


df = get_dataset(
    "market.spy_prices",
    start_date="2026-09-01"
)

print(df.head())
print()

print("Columns:")
print(df.columns.tolist())

silver_path = Path(
    "data/silver/market/spy_prices.parquet"
)

print()
print(
    "Silver file exists:",
    silver_path.exists()
)

print(
    "Silver path:",
    silver_path
)

