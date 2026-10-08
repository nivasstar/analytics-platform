from analytics_platform.policy.source_policy import SourcePolicy


policy = SourcePolicy()

tests = [
    ("population", -1000),
    ("population", 1700),
    ("population", 2025),
    ("gdp", 1700),
    ("gdp", 2025),
]

for metric, year in tests:
    priority = policy.get_priority(
        domain="economic_history",
        metric=metric,
        year=year
    )

    print(
        metric,
        year,
        "->",
        priority
    )
