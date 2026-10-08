from analytics_platform.datasets.gold import build_market_gold


df = build_market_gold(
    start_date="2025-01-01"
)

print(df.tail())

print("\nGold columns:")
print(df.columns.tolist())

latest = df.iloc[-1]

print("\nLatest metrics:")
print("Date:", latest["date"])
print("Close:", latest["close"])
print("200 DMA:", latest["ma_200"])
print("30D Volatility:", latest["volatility_30d"])
print("Drawdown:", latest["drawdown"])
