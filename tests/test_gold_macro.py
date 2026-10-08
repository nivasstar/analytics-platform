from analytics_platform.datasets.gold import build_macro_gold


spread, unemployment = build_macro_gold()

print("Yield Spread:")
print(spread.tail())

print("\nLatest Yield Spread:")
latest_spread = spread.iloc[-1]

print("Date:", latest_spread["date"])
print("10Y:", latest_spread["yield_10y"])
print("3M:", latest_spread["yield_3m"])
print(
    "Spread:",
    latest_spread["yield_spread_10y_3m"]
)

print("\nLatest Unemployment:")
print(unemployment.tail())
