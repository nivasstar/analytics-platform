
from analytics_platform.ingestion.yahoo import YahooSource


source = YahooSource()

df = source.fetch(
    symbol="SPY",
    start_date="2026-09-01"
)

print(df.head())
print()
print(df.columns.tolist())
print()
print(f"Rows returned: {len(df)}")
