import sys

from analytics_platform.reporting.engine import (
    ReportEngine,
)


if len(sys.argv) != 2:
    print(
        "Usage: python run_report.py "
        "config/reports/<report>.yaml"
    )
    sys.exit(1)


engine = ReportEngine(
    sys.argv[1]
)

outputs = engine.run()

print("Report generated:")

for output_type, path in outputs.items():
    if path:
        print(
            f"- {output_type}: {path}"
        )
