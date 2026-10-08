from pathlib import Path
import markdown

from analytics_platform.publishing.theme import SITE_CSS


def publish_html(
    markdown_text,
    output_path,
    title="Analytics Report",
):
    html_body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code"]
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{SITE_CSS}
</style>
</head>

<body>

<nav>
<a href="index.html">Home</a>
<a href="market_risk.html">Market Risk</a>
<a href="economic_history.html">Economic History</a>
</nav>

{html_body}

</body>
</html>
"""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")

    return path
