from analytics_platform.ingestion.registry import DatasetRegistry


registry = DatasetRegistry()

print("Available datasets:")

for dataset in registry.list_datasets():
    print("-", dataset)

print("\nSPY definition:")
print(registry.get("market.spy_prices"))
