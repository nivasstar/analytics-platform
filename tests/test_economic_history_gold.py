from analytics_platform.datasets.gold import (
    build_economic_history_gold,
)


df = build_economic_history_gold(
    country="India"
)

print(df.head(20).to_string(index=False))

print("\nLatest rows:")
print(df.tail(20).to_string(index=False))

print("\nShape:", df.shape)

print("\nYear range:")
print(df["year"].min(), "to", df["year"].max())

print("\nPopulation sources:")
print(df["population_source"].value_counts(dropna=False))

print("\nGDP sources:")
print(df["gdp_source"].value_counts(dropna=False))

print("\nGDP per capita sources:")
print(
    df["gdp_per_capita_source"]
    .value_counts(dropna=False)
)

print(
    "\nDuplicate years:",
    df["year"].duplicated().sum()
)
