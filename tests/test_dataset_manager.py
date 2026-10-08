from analytics_platform.datasets import get_dataset


df = get_dataset(
    "market.spy_prices",
    start_date="2026-09-01"
)

print(df.head())
print()
print(f"Rows returned: {len(df)}")
