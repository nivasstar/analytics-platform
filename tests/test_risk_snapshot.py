from analytics_platform.datasets.gold import build_risk_snapshot


snapshot = build_risk_snapshot()

print("\nMarket Risk Snapshot")
print(snapshot.to_string(index=False))

print("\nColumns:")
print(snapshot.columns.tolist())
