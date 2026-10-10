from analytics_platform.datasets.gold import (
    build_risk_snapshot,
    build_economic_history_gold,
    build_forecasts_vs_facts_gold,
)


BUILDERS = {
    "build_risk_snapshot": build_risk_snapshot,
    "build_economic_history": build_economic_history_gold,
    "build_forecasts_vs_facts": build_forecasts_vs_facts_gold,
}


def get_builder(name):
    if name not in BUILDERS:
        raise ValueError(
            f"Unknown dataset builder: {name}"
        )

    return BUILDERS[name]

from analytics_platform.datasets.gold import (
    build_risk_snapshot,
    build_economic_history_gold,
    build_forecasts_vs_facts_gold,
    build_decisions_vs_outcomes_gold,
)


BUILDERS = {
    "build_risk_snapshot": build_risk_snapshot,
    "build_economic_history": build_economic_history_gold,
    "build_forecasts_vs_facts": build_forecasts_vs_facts_gold,
    "build_decisions_vs_outcomes": build_decisions_vs_outcomes_gold,
}


def get_builder(name):
    if name not in BUILDERS:
        raise ValueError(
            f"Unknown dataset builder: {name}"
        )

    return BUILDERS[name]
