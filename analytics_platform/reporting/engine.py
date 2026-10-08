from pathlib import Path

import yaml

from analytics_platform.reporting.builders import get_builder
from analytics_platform.reporting.renderers import get_renderer
from analytics_platform.publishing.html import publish_html

class ReportEngine:

    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        with open(self.config_path, "r") as file:
            return yaml.safe_load(file)


    def run(self):
        report = self.config["report"]

        builder_name = report["dataset"]["builder"]
        renderer_name = report["renderer"]["type"]

        builder = get_builder(builder_name)
        renderer = get_renderer(renderer_name)

        builder_params = report["dataset"].get(
            "params",
            {}
        )

        dataframe = builder(
            **builder_params
        )

        markdown = renderer(
            report,
            dataframe
        )

        output_path = Path(
            report["output"]["markdown"]
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_config = report["output"]

        markdown_path = None
        html_path = None

        if "markdown" in output_config:
            markdown_path = Path(
                output_config["markdown"]
            )

            markdown_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            markdown_path.write_text(
                markdown,
                encoding="utf-8"
            )

        if "html" in output_config:
            html_path = publish_html(
                markdown_text=markdown,
                output_path=output_config["html"],
                title=report["name"]
            )

        return {
            "markdown": markdown_path,
            "html": html_path,
        }


        return output_path
