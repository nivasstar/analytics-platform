from pathlib import Path

OUTPUT = Path("reports/output")
OUTPUT.mkdir(parents=True, exist_ok=True)

html = """<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Analytics Platform</title>

<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    max-width: 1000px;
    margin: 60px auto;
    padding: 0 24px;
}

h1 {
    margin-bottom: 8px;
}

.card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 22px;
    margin: 20px 0;
}

a {
    text-decoration: none;
}
</style>

</head>

<body>

<h1>Analytics Platform</h1>

<p>
Reusable research, quantitative analysis, and reporting platform.
</p>

<div class="card">
<h2>
<a href="market_risk.html">
Market Risk Monitor
</a>
</h2>

<p>
Market conditions, volatility, drawdown,
yield curve and macroeconomic indicators.
</p>
</div>

<div class="card">
<h2>
<a href="economic_history.html">
Global Economic History
</a>
</h2>

<p>
Long-run population, GDP and GDP-per-capita analysis
across historical and modern data sources.
</p>
</div>

<div class="card">
<h2>
<a href="forecasts_vs_facts.html">
Forecasts vs Facts
</a>
</h2>

<p>
Compare documented economic, technology, energy,
and other forecasts with observed outcomes and supporting evidence.
</p>
</div>

<div class="card">
<h2>
<a href="decisions_vs_outcomes.html">
Debated Decisions vs Outcomes
</a>
</h2>

<p>
Compare claims made during major policy debates with measurable
outcomes observed afterward, while keeping evidence separate from
causal interpretation.
</p>
</div>


<div class="card">
<h2><a href="forecasts_dashboard.html">Interactive Forecasts Explorer</a></h2>
<p>Filter forecasts by category, horizon, region, type and shock context.
Explore linked charts, heatmaps and original evidence.</p>
</div>

</body>
</html>
"""

(OUTPUT / "index.html").write_text(
    html,
    encoding="utf-8"
)

print(
    "Site index generated:",
    OUTPUT / "index.html"
)
