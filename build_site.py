from pathlib import Path

OUT = Path("reports/output")
OUT.mkdir(parents=True, exist_ok=True)

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="A reusable evidence-based analytics and research platform.">
<title>Analytics Platform | Architecture & Use Cases</title>
<style>
:root {
  --navy:#101f37;
  --blue:#4777db;
  --bg:#f5f7fb;
  --ink:#19283e;
  --muted:#617087;
  --line:#dce4ef;
}
* {box-sizing:border-box}
body {
  margin:0;background:var(--bg);color:var(--ink);
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  line-height:1.6;
}
header {
  background:linear-gradient(125deg,#101f37,#1d3c65);
  color:white;padding:34px max(5%,calc((100vw - 1160px)/2));
}
header .eyebrow {
  font-size:12px;letter-spacing:2px;text-transform:uppercase;
  color:#a5c7fb;font-weight:700;
}
header h1 {font-size:clamp(30px,4vw,48px);margin:9px 0}
header p {max-width:780px;color:#d7e4f8;margin:0}
nav {
  background:white;border-bottom:1px solid var(--line);
  position:sticky;top:0;z-index:10;
}
.nav-inner {
  max-width:1200px;margin:auto;display:flex;gap:8px;padding:10px 20px;
}
.tab {
  border:0;background:transparent;border-radius:9px;
  padding:12px 22px;cursor:pointer;font-size:15px;
  color:#53647d;font-weight:650;
}
.tab.active {background:#eaf1ff;color:#174b9b}
.tab:focus-visible,a:focus-visible {outline:3px solid #81b2ff;outline-offset:2px}
main {max-width:1200px;margin:auto;padding:34px 20px 65px}
.panel[hidden] {display:none}
.section-title {font-size:25px;margin:34px 0 9px}
.lead {color:var(--muted);max-width:850px;margin-bottom:25px}
.card {
  background:white;border:1px solid var(--line);
  border-radius:14px;padding:23px;
}
.hero {
  display:grid;grid-template-columns:1.5fr 1fr;gap:18px;
}
.hero h2 {font-size:27px;line-height:1.3;margin:0 0 14px}
.hero p {color:var(--muted);margin:0}
.hero-side {
  background:#eaf1ff;border-radius:12px;
  padding:22px;display:flex;flex-direction:column;justify-content:center;
}
.hero-side strong {font-size:19px}
.hero-side span {font-size:14px;color:#4f617b;margin-top:9px}
.pipeline {
  display:flex;align-items:stretch;gap:8px;
  margin:25px 0;overflow-x:auto;padding:3px 2px 13px;
}
.step {
  flex:1;min-width:128px;background:white;
  border:1px solid var(--line);border-top:4px solid var(--blue);
  padding:16px 10px;border-radius:11px;text-align:center;
}
.step small {
  display:block;color:var(--muted);
  line-height:1.45;margin-top:8px;font-size:12px;
}
.step .symbol {font-size:25px;margin-bottom:7px}
.arrow {
  align-self:center;font-size:21px;font-weight:700;
  color:#7392c6;flex-shrink:0;
}
.caption {font-size:13px;color:var(--muted)}
.grid {
  display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;
}
.grid.two {grid-template-columns:repeat(2,minmax(0,1fr))}
.layer h3,.usecase h3 {margin:0 0 9px;font-size:19px}
.layer p,.usecase p {color:var(--muted);font-size:14px;margin:0}
.tag {
  display:inline-block;background:#edf3ff;color:#28549a;
  border-radius:20px;padding:4px 11px;font-size:12px;
  margin-bottom:12px;font-weight:700;
}
.lifecycle {
  display:flex;flex-wrap:wrap;align-items:center;gap:10px;
  background:white;border:1px solid var(--line);
  padding:22px;border-radius:14px;
}
.lifecycle span {
  background:#eff4fb;padding:11px 14px;border-radius:9px;
  font-size:13px;font-weight:650;
}
.lifecycle b {color:#6a88ba}
.note {
  background:#eef3fa;border-left:4px solid var(--blue);
  padding:17px 21px;border-radius:8px;color:#43566f;margin-top:22px;
}
.usecase {display:flex;flex-direction:column;gap:12px}
.usecase .actions {display:flex;gap:10px;flex-wrap:wrap;margin-top:auto}
a.btn {
  display:inline-block;text-decoration:none;
  border-radius:8px;padding:10px 14px;font-size:13px;
  font-weight:700;background:#1a4c98;color:white;
}
a.btn.secondary {
  background:#edf3fc;color:#245393;
  border:1px solid #d3e1f6;
}
a.btn:hover {filter:brightness(.94)}
details {
  background:white;border:1px solid var(--line);
  border-radius:12px;padding:17px 20px;margin-top:12px;
}
summary {font-weight:700;cursor:pointer}
details p {color:var(--muted)}
footer {
  text-align:center;background:#101f37;color:#c8d5e7;
  padding:24px;font-size:13px;
}
@media(max-width:850px) {
  .hero,.grid,.grid.two {grid-template-columns:1fr}
  .pipeline {flex-wrap:wrap}
  .step {flex:1 1 28%}
  .arrow {transform:rotate(90deg)}
}
@media(max-width:500px) {
  .step {flex:1 1 100%}
  .arrow {width:100%;text-align:center}
  main {padding:22px 14px 45px}
  header {padding:30px 18px}
  .nav-inner {padding:8px 12px}
  .tab {flex:1;padding:10px}
}
</style>
</head>

<body>
<header>
  <div class="eyebrow">Reusable Analytics & Research Infrastructure</div>
  <h1>Analytics Platform</h1>
  <p>
    From data ingestion to evidence-based insights.
    A modular research platform integrating data engineering,
    quantitative analytics, historical research, and interactive reporting.
  </p>
</header>

<nav aria-label="Main navigation">
  <div class="nav-inner" role="tablist">
    <button class="tab active" id="overview-tab" role="tab"
      aria-controls="overview" aria-selected="true"
      data-tab="overview">01 — Architecture</button>
    <button class="tab" id="usecases-tab" role="tab"
      aria-controls="usecases" aria-selected="false"
      data-tab="usecases">02 — Use Cases</button>
  </div>
</nav>

<main>
<section id="overview" class="panel" role="tabpanel" aria-labelledby="overview-tab">

  <div class="hero">
    <div class="card">
      <div class="tag">Platform Overview</div>
      <h2>One architecture. Multiple analytical domains.</h2>
      <p>
        The platform separates acquisition, storage, data quality,
        transformation, analytics, and publication into reusable layers.
        Market risk, economic history, forecasts, and public policy
        comparisons can share the same infrastructure while retaining
        their own analytical logic and sources.
      </p>
    </div>
    <div class="hero-side">
      <strong>From source data to published research</strong>
      <span>Python + Parquet for processing</span>
      <span>Reusable Bronze / Silver / Gold datasets</span>
      <span>Plotly dashboards and HTML reports</span>
      <span>GitHub Actions and GitHub Pages delivery</span>
    </div>
  </div>

  <h2 class="section-title">End-to-end data architecture</h2>
  <p class="lead">
    Each stage has a distinct responsibility, allowing new topics and
    datasets to enter the platform without rebuilding the whole pipeline.
  </p>

  <div class="pipeline" role="img"
       aria-label="Sources flow through ingestion, Bronze, Silver, Gold, analytics and interactive publishing">
    <div class="step">
      <div class="symbol">🌐</div><strong>Sources</strong>
      <small>Yahoo Finance, FRED, historical files, curated CSV</small>
    </div>
    <div class="arrow" aria-hidden="true">→</div>
    <div class="step">
      <div class="symbol">🔌</div><strong>Ingestion</strong>
      <small>Adapters, dataset registry, source-specific loading</small>
    </div>
    <div class="arrow" aria-hidden="true">→</div>
    <div class="step">
      <div class="symbol">🥉</div><strong>Bronze</strong>
      <small>Persisted source data and ingestion metadata</small>
    </div>
    <div class="arrow" aria-hidden="true">→</div>
    <div class="step">
      <div class="symbol">🥈</div><strong>Silver</strong>
      <small>Normalized schemas, dates and validated records</small>
    </div>
    <div class="arrow" aria-hidden="true">→</div>
    <div class="step">
      <div class="symbol">🥇</div><strong>Gold</strong>
      <small>Curated metrics, comparisons and analytical tables</small>
    </div>
    <div class="arrow" aria-hidden="true">→</div>
    <div class="step">
      <div class="symbol">📊</div><strong>Publish</strong>
      <small>Research reports and interactive dashboards</small>
    </div>
  </div>

  <p class="caption">
    Conceptual flow: actual transformations vary by dataset.
    Domain-specific analytics operate on curated data before publication.
  </p>

  <h2 class="section-title">Platform components</h2>
  <div class="grid">
    <article class="card layer">
      <div class="tag">01 · Data acquisition</div>
      <h3>Dataset registry & adapters</h3>
      <p>
        Dataset definitions identify available sources. Yahoo and FRED
        adapters, along with local Parquet and CSV ingestion, support
        different source structures through a common pipeline.
      </p>
    </article>
    <article class="card layer">
      <div class="tag">02 · Data engineering</div>
      <h3>Bronze, Silver & Gold</h3>
      <p>
        Source observations are persisted, standardized and shaped into
        analytical datasets. Gold tables support reusable calculations
        such as volatility, yield spreads, and historical timelines.
      </p>
    </article>
    <article class="card layer">
      <div class="tag">03 · Quality</div>
      <h3>Validation & provenance</h3>
      <p>
        Schema and data checks help catch unusable observations.
        Source identifiers, publication dates and evidence references
        make analytical results easier to inspect and verify.
      </p>
    </article>
    <article class="card layer">
      <div class="tag">04 · Analytics</div>
      <h3>Domain-specific models</h3>
      <p>
        Dedicated Python modules handle market indicators,
        macroeconomic signals, economic history, forecast errors,
        and policy claim comparisons.
      </p>
    </article>
    <article class="card layer">
      <div class="tag">05 · Experience</div>
      <h3>Interactive research</h3>
      <p>
        HTML and Plotly provide browser-based filtering, chart
        exploration and source-level evidence inspection.
        Static reports remain available alongside dashboards.
      </p>
    </article>
    <article class="card layer">
      <div class="tag">06 · Delivery</div>
      <h3>Automated publishing</h3>
      <p>
        GitHub Actions runs the configured reporting build and
        publishes generated HTML assets to GitHub Pages.
        The deployment workflow is reproducible from source code.
      </p>
    </article>
  </div>

  <h2 class="section-title">Build and delivery lifecycle</h2>
  <div class="lifecycle">
    <span>Git repository</span><b>→</b>
    <span>GitHub Actions</span><b>→</b>
    <span>Python pipelines</span><b>→</b>
    <span>Data & report generation</span><b>→</b>
    <span>GitHub Pages</span>
  </div>

  <h2 class="section-title">Research design principles</h2>

  <details open>
    <summary>Evidence before interpretation</summary>
    <p>
      Forecasts are compared with documented outcomes, while historical
      policy claims are retained separately from later evidence and
      causal interpretation. Sources and assumptions should remain visible.
    </p>
  </details>
  <details>
    <summary>Comparability and historical uncertainty</summary>
    <p>
      Units, geographic definitions, time horizons, estimation methods
      and missing observations can materially affect comparisons.
      Historical estimates should not be presented as precise measurements
      where the underlying sources do not support that precision.
    </p>
  </details>
  <details>
    <summary>Modularity and extensibility</summary>
    <p>
      New research areas can add dataset configurations, source adapters,
      analytical builders and dashboards while reusing existing data
      storage, reporting, and deployment patterns.
    </p>
  </details>

  <div class="note">
    <strong>Current hosting:</strong> GitHub Pages serves this site
    publicly. Published datasets and embedded dashboard records
    should therefore contain only information suitable for public access.
  </div>
</section>

<section id="usecases" class="panel" role="tabpanel"
         aria-labelledby="usecases-tab" hidden>
  <h2 class="section-title" style="margin-top:0">Research Use Cases</h2>
  <p class="lead">
    Four analytical domains built on the same reusable platform.
    Each provides an interactive explorer and a supporting report.
  </p>

  <div class="grid two">
    <article class="card usecase">
      <div class="tag">Forecasting & Prediction</div>
      <h3>Forecasts vs Facts</h3>
      <p>
        Compare documented forecasts with realized outcomes.
        Explore categories, geography, forecast horizon and shock context,
        while reviewing primary evidence and numeric deviations.
      </p>
      <div class="actions">
        <a class="btn" href="forecasts_dashboard.html">Interactive dashboard ↗</a>
        <a class="btn secondary" href="forecasts_vs_facts.html">Research report</a>
      </div>
    </article>

    <article class="card usecase">
      <div class="tag">Public Policy & Evidence</div>
      <h3>Debated Decisions vs Outcomes</h3>
      <p>
        Investigate claims made during policy debates and compare
        them with subsequently reported outcomes.
        Distinguish original expectations from evidence and interpretation.
      </p>
      <div class="actions">
        <a class="btn" href="decisions_dashboard.html">Interactive dashboard ↗</a>
        <a class="btn secondary" href="decisions_vs_outcomes.html">Research report</a>
      </div>
    </article>

    <article class="card usecase">
      <div class="tag">Long-run Economic Research</div>
      <h3>Global Economic History</h3>
      <p>
        Explore economic development over centuries.
        Compare countries, inspect population, GDP and
        GDP per capita where supported by historical sources.
      </p>
      <div class="actions">
        <a class="btn" href="economic_dashboard.html">Interactive dashboard ↗</a>
        <a class="btn secondary" href="economic_history.html">Research report</a>
      </div>
    </article>

    <article class="card usecase">
      <div class="tag">Financial Markets & Macro Risk</div>
      <h3>Market Risk Monitor</h3>
      <p>
        Review SPY market trends, moving averages, volatility,
        drawdowns, Treasury yield spreads and unemployment
        over selectable time windows.
      </p>
      <div class="actions">
        <a class="btn" href="market_dashboard.html">Interactive dashboard ↗</a>
        <a class="btn secondary" href="market_risk.html">Research report</a>
      </div>
    </article>
  </div>

  <div class="note">
    The interactive dashboards are exploratory tools.
    They do not substitute for evaluation of source methodology,
    data quality, uncertainty or causal assumptions.
  </div>
</section>
</main>

<footer>
  Analytics Platform · Modular Data Engineering · Quantitative Research ·
  Evidence-Based Reporting
</footer>

<script>
(function(){
 const tabs=[...document.querySelectorAll(".tab")];
 const panels=[...document.querySelectorAll(".panel")];

 function activate(name,changeHash){
  const selected=name==="usecases"?"usecases":"overview";
  tabs.forEach(tab=>{
   const active=tab.dataset.tab===selected;
   tab.classList.toggle("active",active);
   tab.setAttribute("aria-selected",String(active));
   tab.tabIndex=active?0:-1;
  });
  panels.forEach(panel=>{
   panel.hidden=panel.id!==selected;
  });
  if(changeHash)history.replaceState(null,"","#"+selected);
 }

 tabs.forEach(tab=>{
  tab.addEventListener("click",()=>activate(tab.dataset.tab,true));
  tab.addEventListener("keydown",event=>{
   if(event.key==="ArrowLeft"||event.key==="ArrowRight"){
    event.preventDefault();
    const next=tab.dataset.tab==="overview"?"usecases":"overview";
    activate(next,true);
    document.querySelector('[data-tab="'+next+'"]').focus();
   }
  });
 });
 window.addEventListener("hashchange",()=>activate(location.hash.slice(1),false));
 activate(location.hash.slice(1),false);
})();
</script>
</body>
</html>
'''

target = OUT / "index.html"
target.write_text(html, encoding="utf-8")

print("Homepage generated:", target)
print("Tabs: Architecture | Use Cases")
print("Dashboard links: 4")
print("Research report links: 4")
