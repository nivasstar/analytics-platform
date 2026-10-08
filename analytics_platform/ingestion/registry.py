from pathlib import Path
import yaml


class DatasetRegistry:

    def __init__(self, registry_path="config/datasets.yaml"):
        self.registry_path = Path(registry_path)
        self.datasets = self._load()

    def _load(self):
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"Dataset registry not found: {self.registry_path}"
            )

        with open(self.registry_path, "r") as file:
            config = yaml.safe_load(file) or {}

        return config.get("datasets", {})

    def get(self, dataset_name):
        if dataset_name not in self.datasets:
            raise KeyError(
                f"Dataset '{dataset_name}' not found in registry"
            )

        return self.datasets[dataset_name]

    def list_datasets(self):
        return list(self.datasets.keys())
