from analytics_platform.datasets.gold import (
    build_risk_snapshot,
    build_economic_history_gold,
)


BUILDERS = {
    "build_risk_snapshot": build_risk_snapshot,
    "build_economic_history": build_economic_history_gold,
}


def get_builder(name):
    if name not in BUILDERS:
        raise ValueError(
            f"Unknown dataset builder: {name}"
        )

    return BUILDERS[name]
