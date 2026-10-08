from pathlib import Path
import yaml


class SourcePolicy:

    def __init__(self, path="config/source_policies.yaml"):
        self.path = Path(path)

        with open(self.path, "r") as file:
            self.config = yaml.safe_load(file) or {}

    def get_priority(
        self,
        domain,
        metric,
        year
    ):
        metric_config = (
            self.config
            .get(domain, {})
            .get(metric, {})
        )

        rules = metric_config.get("rules", [])

        for rule in rules:
            start = rule.get("from")
            end = rule.get("before")

            if start is not None and year < start:
                continue

            if end is not None and year >= end:
                continue

            return rule.get("priority", [])

        return []
