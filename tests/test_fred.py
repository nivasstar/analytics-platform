from analytics_platform.datasets import get_dataset


unemployment = get_dataset("macro.unemployment")
yield_10y = get_dataset("macro.yield_10y")

print("Unemployment:")
print(unemployment.head())

print("\n10Y Treasury:")
print(yield_10y.head())

