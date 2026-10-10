from pathlib import Path
import json

from analytics_platform.datasets.gold import (
    build_forecasts_vs_facts_gold,
)

output = Path("reports/output")
output.mkdir(parents=True, exist_ok=True)

df = build_forecasts_vs_facts_gold()

# Convert dates and nullable numeric fields safely to JSON.
records = json.loads(
    df.to_json(orient="records", date_format="iso")
)

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Forecasts vs Facts | Interactive Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {
  font-family: system-ui, Arial, sans-serif;
  color: #172338;
  background: #f5f7fb;
}
body { margin: 0; }
header {
  background: #142741;
  color: white;
  padding: 24px 5%;
}
header a { color: #c4dfff; }
main { max-width: 1400px; margin: auto; padding: 24px; }
.filters, .stats, .charts { display: grid; gap: 14px; }
.filters { grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); }
.stats { grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); margin:20px 0; }
.charts { grid-template-columns: repeat(auto-fit,minmax(420px,1fr)); }
.card {
  background: white;
  border: 1px solid #e2e6ee;
  border-radius: 12px;
  padding: 16px;
  min-width: 0;
}
label { display:block; font-size:13px; margin-bottom:6px; }
select,input {
  width:100%;
  padding:10px;
  box-sizing:border-box;
  border:1px solid #ccd3df;
  border-radius:7px;
  background:white;
}
.stat { font-size:27px; font-weight:700; margin-top:6px; }
.muted { color:#596579; font-size:13px; }
.chart { height:370px; }
.wide { grid-column:1/-1; }
.tablewrap { overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th,td { padding:11px; border-bottom:1px solid #e5e8ee; text-align:left; }
th { background:#f1f4f9; }
td { vertical-align:top; }
footer { padding:25px; text-align:center; font-size:12px; color:#677; }
@media(max-width:600px) {
  main {padding:12px;}
  .charts {grid-template-columns:1fr;}
  .chart {height:310px;}
}
</style>
</head>
<body>
<header>
  <a href="index.html">← Analytics Platform</a>
  <h1>Forecasts vs Facts</h1>
  <p>Interactive evidence-based forecast comparisons</p>
</header>

<main>
<section class="card">
  <h3>Explore the data</h3>
  <div class="filters">
    <div><label>Category</label><select id="category"></select></div>
    <div><label>Forecast type</label><select id="type"></select></div>
    <div><label>Region</label><select id="region"></select></div>
    <div><label>Horizon</label><select id="horizon"></select></div>
    <div><label>Shock context</label><select id="shock"></select></div>
    <div><label>Search topic</label><input id="search" placeholder="GDP, solar, EV..."></div>
  </div>
</section>

<section class="stats">
  <div class="card"><div class="muted">Comparisons</div><div id="count" class="stat">—</div></div>
  <div class="card"><div class="muted">Mean absolute % error</div><div id="mae" class="stat">—</div></div>
  <div class="card"><div class="muted">Median absolute % error</div><div id="median" class="stat">—</div></div>
  <div class="card"><div class="muted">Categories</div><div id="categories" class="stat">—</div></div>
</section>

<section class="charts">
  <div class="card"><h3>Largest forecast misses</h3><div id="errors" class="chart"></div></div>
  <div class="card"><h3>Accuracy by forecast horizon</h3><div id="horizons" class="chart"></div></div>
  <div class="card wide"><h3>Category × horizon heatmap</h3><div id="heatmap" class="chart"></div></div>
</section>

<section class="card" style="margin-top:20px">
  <h3>Underlying evidence and comparisons</h3>
  <p class="muted">Click a source link to inspect the original publication. Errors are computed only for eligible numeric point forecasts.</p>
  <div class="tablewrap">
    <table>
      <thead><tr>
        <th>Topic</th><th>Type</th><th>Forecast date</th>
        <th>Target</th><th>Horizon</th><th>Forecast</th>
        <th>Actual</th><th>Error</th><th>Evidence</th>
      </tr></thead>
      <tbody id="table"></tbody>
    </table>
  </div>
</section>
</main>
<footer>Analytics Platform · Forecasts vs Facts · Descriptive analysis, not causal attribution</footer>

<script>
const DATA = __ROWS__;
const $ = id => document.getElementById(id);
const buckets = ["<1 year","1–3 years","3–10 years","10+ years"];

function horizon(r) {
  const y = Number(r.forecast_horizon_years);
  if (r.forecast_horizon_years == null || !Number.isFinite(y)) return "Unknown";
  return y < 1 ? buckets[0] : y < 3 ? buckets[1] : y < 10 ? buckets[2] : buckets[3];
}
function error(r) {
  if (r.forecast_operator !== "eq") return null;
  const a = Number(r.actual_value), f = Number(r.forecast_value);
  if (r.actual_value == null || r.forecast_value == null ||
      !Number.isFinite(a) || !Number.isFinite(f) || f === 0) return null;
  return Math.abs((a-f)/f)*100;
}
function avg(a) {return a.length?a.reduce((x,y)=>x+y,0)/a.length:null;}
function median(a) {
  if (!a.length) return null;
  const s=[...a].sort((x,y)=>x-y), k=Math.floor(s.length/2);
  return s.length%2?s[k]:(s[k-1]+s[k])/2;
}
function fmt(v) {return v==null?"—":Number(v).toFixed(1)+"%";}
function esc(v) {
  return String(v??"—").replace(/[&<>"']/g,c=>({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  })[c]);
}
function link(url,label) {
  if (!/^https:\/\//i.test(url??"")) return "—";
  return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
}
function options(id,values) {
  const sel=$(id);
  sel.innerHTML="";
  ["All",...new Set(values.filter(v=>v!=null).map(String))].sort((a,b)=>
    a==="All"?-1:b==="All"?1:a.localeCompare(b)
  ).forEach(v=>{
    const o=document.createElement("option");
    o.value=v;o.textContent=v;sel.appendChild(o);
  });
}
options("category",DATA.map(r=>r.category));
options("type",DATA.map(r=>r.forecast_type||"forecast"));
options("region",DATA.map(r=>r.region||"Unspecified"));
options("horizon",DATA.map(horizon));
options("shock",DATA.map(r=>r.shock_context||"Unspecified"));

function matches(v,selected) {return selected==="All"||String(v)===selected;}
const layout={margin:{l:65,r:20,t:12,b:60},paper_bgcolor:"white",
  plot_bgcolor:"white",font:{family:"Arial",size:12}};
const config={responsive:true,displaylogo:false};

function update() {
  const rows=DATA.filter(r=>
    matches(r.category,$("category").value) &&
    matches(r.forecast_type||"forecast",$("type").value) &&
    matches(r.region||"Unspecified",$("region").value) &&
    matches(horizon(r),$("horizon").value) &&
    matches(r.shock_context||"Unspecified",$("shock").value) &&
    String(r.topic||"").toLowerCase().includes($("search").value.toLowerCase())
  );

  const scored=rows.map(r=>({...r,ape:error(r)})).filter(r=>r.ape!=null);
  const values=scored.map(r=>r.ape);
  $("count").textContent=rows.length;
  $("mae").textContent=fmt(avg(values));
  $("median").textContent=fmt(median(values));
  $("categories").textContent=new Set(rows.map(r=>r.category)).size;

  const largest=[...scored].sort((a,b)=>b.ape-a.ape).slice(0,15).reverse();
  Plotly.react("errors",[{
    type:"bar",orientation:"h",
    x:largest.map(r=>r.ape),
    y:largest.map(r=>r.forecast_id),
    hovertext:largest.map(r=>r.topic),
    hovertemplate:"%{hovertext}<br>Error: %{x:.1f}%<extra></extra>"
  }],{...layout,xaxis:{title:"Absolute percentage error"}},config);

  const counts=buckets.map(b=>scored.filter(r=>horizon(r)===b));
  Plotly.react("horizons",[{
    type:"bar",x:buckets,y:counts.map(a=>avg(a.map(r=>r.ape))),
    text:counts.map(a=>"n="+a.length),textposition:"outside",
    hovertemplate:"%{x}<br>Mean error: %{y:.1f}%<extra></extra>"
  }],{...layout,yaxis:{title:"Mean absolute percentage error"}},config);

  const cats=[...new Set(scored.map(r=>r.category))].sort();
  const z=cats.map(c=>buckets.map(b=>avg(
    scored.filter(r=>r.category===c&&horizon(r)===b).map(r=>r.ape)
  )));
  Plotly.react("heatmap",[{
    type:"heatmap",x:buckets,y:cats,z,
    colorscale:"Blues",
    hovertemplate:"%{y} · %{x}<br>Mean error: %{z:.1f}%<extra></extra>"
  }],{...layout,margin:{l:150,r:25,t:15,b:65}},config);

  $("table").innerHTML=rows.map(r=>{
    let prediction=esc(r.forecast_value);
    if (r.forecast_operator==="gt") prediction="&gt; "+prediction;
    if (r.forecast_operator==="lt") prediction="&lt; "+prediction;
    if (r.forecast_operator==="range")
      prediction=esc(r.forecast_lower)+"–"+esc(r.forecast_upper);
    return `<tr>
      <td>${esc(r.topic)}</td><td>${esc(r.forecast_type||"forecast")}</td>
      <td>${esc(String(r.forecast_date||"").slice(0,10))}</td>
      <td>${esc(String(r.target_date||"").slice(0,10))}</td>
      <td>${esc(horizon(r))}</td><td>${prediction}</td>
      <td>${esc(r.actual_value)}</td><td>${fmt(error(r))}</td>
      <td>${link(r.forecast_url,"Forecast")} · ${link(r.actual_url,"Actual")}</td>
    </tr>`;
  }).join("");
}
["category","type","region","horizon","shock","search"].forEach(id=>
  $(id).addEventListener(id==="search"?"input":"change",update)
);
update();
</script>
</body>
</html>
"""

safe_json = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
html = html.replace("__ROWS__", safe_json)

target = output / "forecasts_dashboard.html"
target.write_text(html, encoding="utf-8")
print(f"Interactive dashboard generated: {target}")
print(f"Records: {len(records)}")
