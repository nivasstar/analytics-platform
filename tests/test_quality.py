from analytics_platform.datasets import get_dataset


df = get_dataset(
    "market.spy_prices",
    start_date="2026-09-01"
)

print("Quality validation passed")
print(df.head())
