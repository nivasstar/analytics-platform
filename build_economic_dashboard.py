from pathlib import Path
import json
import pandas as pd

BASE = Path("data/external/economic_history")
OUT = Path("reports/output")
OUT.mkdir(parents=True, exist_ok=True)

FILES = [
    BASE / "country_history.parquet",
    BASE / "long_population.parquet",
]

ALIASES = {
    "country": ["country", "country_name", "entity", "location", "nation"],
    "year": ["year", "year_ce", "historical_year"],
    "population": ["population", "population_total", "pop", "pop_total"],
    "gdp_per_capita": [
        "gdp_per_capita", "gdp_pc", "gdppc",
        "gdp_per_capita_intl_dollars", "gdp_per_capita_2011",
    ],
    "gdp": ["gdp", "total_gdp", "gdp_total"],
}

def find_column(df, choices):
    columns = {str(c).strip().lower(): c for c in df.columns}
    for name in choices:
        if name in columns:
            return columns[name]
    return None

frames = []

for file in FILES:
    if not file.exists():
        print("Not found, skipping:", file)
        continue

    raw = pd.read_parquet(file)
    print(f"\n{file}: {len(raw)} rows")
    print("Columns:", list(raw.columns))

    country_col = find_column(raw, ALIASES["country"])
    year_col = find_column(raw, ALIASES["year"])

    if country_col is None or year_col is None:
        print("Skipping: country/year columns not identified")
        continue

    for metric in ["population", "gdp_per_capita", "gdp"]:
        value_col = find_column(raw, ALIASES[metric])
        if value_col is None:
            continue

        source_col = find_column(
            raw, ["source", "source_name", "citation", "dataset_source"]
        )

        normalized = pd.DataFrame({
            "country": raw[country_col].astype("string"),
            "year": pd.to_numeric(raw[year_col], errors="coerce"),
            "metric": metric,
            "value": pd.to_numeric(raw[value_col], errors="coerce"),
            "source": (
                raw[source_col].astype("string")
                if source_col is not None
                else file.stem
            ),
            "dataset": file.stem,
        })

        frames.append(normalized)

if not frames:
    raise SystemExit(
        "No compatible data found. Review the printed Parquet column names."
    )

data = pd.concat(frames, ignore_index=True)
data = data.dropna(subset=["country", "year", "value"])
data = data[data["country"].str.strip() != ""]
data["year"] = data["year"].astype(int)
data["country"] = data["country"].astype(str)
data["source"] = data["source"].fillna("Unspecified").astype(str)

# Preserve source priority: country_history first, then long_population
# for country/year/metric combinations not already represented.
data = data.drop_duplicates(
    subset=["country", "year", "metric"], keep="first"
)
data = data.sort_values(["country", "metric", "year"])

if data.empty:
    raise SystemExit("No usable historical observations found.")

records = json.loads(data.to_json(orient="records"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Global Economic History | Interactive Explorer</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f5f7fb;color:#18263b;font-family:system-ui,Arial}
header{background:#142741;color:white;padding:26px 5%}
header a{color:#c5ddff}
main{max-width:1450px;margin:auto;padding:24px}
.card{background:white;border:1px solid #e0e5ed;border-radius:12px;padding:18px;min-width:0}
.filters,.stats{display:grid;gap:15px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.stats{margin:20px 0}
label{display:block;font-size:13px;margin-bottom:7px}
select,input{width:100%;padding:10px;border:1px solid #cbd3df;border-radius:7px;background:white}
input[type=range]{padding:0;accent-color:#315b9e}
.stat{font-size:24px;font-weight:700;margin-top:7px}
.muted{font-size:13px;color:#637189}
.chart{height:490px}
.timeline{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:18px}
.tablewrap{overflow-x:auto;max-height:480px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px;border-bottom:1px solid #e5e8ef;text-align:left}
th{position:sticky;top:0;background:#f1f4f9}
footer{text-align:center;padding:25px;color:#697789;font-size:12px}
@media(max-width:650px){
 main{padding:12px}
 .timeline{grid-template-columns:1fr}
 .chart{height:340px}
}
</style>
</head>
<body>
<header>
<a href="index.html">← Analytics Platform</a>
<h1>Global Economic History</h1>
<p>Explore population and economic development across countries and centuries.</p>
</header>
<main>
<section class="card">
<h3>Choose your comparison</h3>
<div class="filters">
<div><label>Primary country</label><select id="primary"></select></div>
<div><label>Compare with</label><select id="compare"></select></div>
<div><label>Metric</label><select id="metric"></select></div>
<div><label>Scale</label>
<select id="scale">
<option value="linear">Linear</option>
<option value="log">Logarithmic (positive values only)</option>
</select></div>
</div>
<div class="timeline">
<div><label>Start year: <strong id="startLabel"></strong></label>
<input type="range" id="start"></div>
<div><label>End year: <strong id="endLabel"></strong></label>
<input type="range" id="end"></div>
</div>
<p class="muted">Negative years represent BCE. Each point represents a recorded or estimated observation, not necessarily annual data.</p>
</section>

<section class="stats">
<div class="card"><div class="muted">Primary latest observation</div><div id="primaryValue" class="stat">—</div><div id="primaryDate" class="muted"></div></div>
<div class="card"><div class="muted">Comparison latest observation</div><div id="compareValue" class="stat">—</div><div id="compareDate" class="muted"></div></div>
<div class="card"><div class="muted">Observations shown</div><div id="records" class="stat">—</div></div>
<div class="card"><div class="muted">Historical coverage</div><div id="coverage" class="stat">—</div></div>
</section>

<section class="card">
<h3 id="chartTitle">Historical development</h3>
<div id="chart" class="chart"></div>
<p class="muted">Lines connect available observations for readability. They do not imply that values between observations were measured.</p>
</section>

<section class="card" style="margin-top:20px">
<h3>Underlying observations</h3>
<p class="muted">Sources are reported as provided by the underlying datasets. Units should be verified against the original methodology before making cross-source or monetary comparisons.</p>
<div class="tablewrap">
<table>
<thead><tr><th>Country</th><th>Year</th><th>Metric</th><th>Value</th><th>Source</th><th>Dataset</th></tr></thead>
<tbody id="table"></tbody>
</table>
</div>
</section>
</main>
<footer>Analytics Platform · Historical estimates contain uncertainty and uneven source coverage</footer>
<script>
const DATA=__DATA__;
const $=id=>document.getElementById(id);
const metricLabels={
 population:"Population",
 gdp_per_capita:"GDP per capita (source units)",
 gdp:"Total GDP (source units)"
};
const esc=v=>String(v??"—").replace(/[&<>"']/g,c=>({
 "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
})[c]);
const fmt=v=>Number(v).toLocaleString("en-US",{maximumFractionDigits:2});
const yearLabel=y=>y<0?`${Math.abs(y)} BCE`:y===0?"Year 0":`${y} CE`;
const countries=[...new Set(DATA.map(r=>r.country))].sort();
const metrics=[...new Set(DATA.map(r=>r.metric))].sort();
const years=DATA.map(r=>r.year);
const minYear=Math.min(...years),maxYear=Math.max(...years);

function addOptions(id,values){
 $(id).innerHTML="";
 values.forEach(v=>{
  const el=document.createElement("option");
  el.value=v;el.textContent=v;$(id).appendChild(el);
 });
}
addOptions("primary",countries);
addOptions("compare",["None",...countries]);
addOptions("metric",metrics.map(m=>m));
[...$("metric").options].forEach(o=>o.textContent=metricLabels[o.value]||o.value);

function choose(names,fallback){
 return names.find(n=>countries.some(c=>c.toLowerCase()===n.toLowerCase()))||fallback;
}
$("primary").value=choose(["India"],countries[0]);
$("compare").value=choose(["China"],"None");
if($("compare").value===$("primary").value)$("compare").value="None";
$("metric").value=metrics.includes("population")?"population":metrics[0];

for(const id of ["start","end"]){
 $(id).min=minYear;$(id).max=maxYear;$(id).step=1;
}
$("start").value=Math.max(minYear,1000);
$("end").value=maxYear;

const config={responsive:true,displaylogo:false,scrollZoom:true};
function refresh(changed){
 let start=Number($("start").value),end=Number($("end").value);
 if(start>end){
  if(changed==="start")$("end").value=start;
  else $("start").value=end;
  start=Number($("start").value);end=Number($("end").value);
 }
 $("startLabel").textContent=yearLabel(start);
 $("endLabel").textContent=yearLabel(end);

 const metric=$("metric").value;
 const primary=$("primary").value;
 const compare=$("compare").value;
 const selected=[primary,...(compare!=="None"&&compare!==primary?[compare]:[])];
 const scale=$("scale").value;

 const rows=DATA.filter(r=>
  selected.includes(r.country)&&r.metric===metric&&
  r.year>=start&&r.year<=end&&
  (scale!=="log"||r.value>0)
 ).sort((a,b)=>a.year-b.year);

 const traces=selected.map(country=>{
  const points=rows.filter(r=>r.country===country);
  return {
   type:"scatter",mode:"lines+markers",name:country,
   x:points.map(r=>r.year),y:points.map(r=>r.value),
   text:points.map(r=>r.source),
   customdata:points.map(r=>r.dataset),
   hovertemplate:"%{fullData.name}<br>Year: %{x}<br>Value: %{y:,.2f}<br>Source: %{text}<br>Dataset: %{customdata}<extra></extra>",
   connectgaps:false
  };
 });

 $("chartTitle").textContent=(metricLabels[metric]||metric)+" — historical comparison";
 Plotly.react("chart",traces,{
  margin:{l:90,r:30,t:20,b:75},
  paper_bgcolor:"white",plot_bgcolor:"white",
  font:{family:"Arial",size:12},
  xaxis:{title:"Year (negative = BCE)",range:[start,end],zeroline:true},
  yaxis:{title:metricLabels[metric]||metric,type:scale},
  hovermode:"closest",
  legend:{orientation:"h",y:1.15}
 },config);

 function latest(country){
  const points=rows.filter(r=>r.country===country);
  return points.length?points[points.length-1]:null;
 }
 const first=latest(primary),second=compare==="None"?null:latest(compare);
 $("primaryValue").textContent=first?fmt(first.value):"—";
 $("primaryDate").textContent=first?primary+" · "+yearLabel(first.year):"No observations";
 $("compareValue").textContent=second?fmt(second.value):"—";
 $("compareDate").textContent=second?compare+" · "+yearLabel(second.year):"No comparison observations";
 $("records").textContent=rows.length.toLocaleString();
 $("coverage").textContent=rows.length?
  yearLabel(rows[0].year)+" – "+yearLabel(rows[rows.length-1].year):"—";

 // Limit visible table rows for browser responsiveness.
 $("table").innerHTML=rows.slice(0,1500).map(r=>`
 <tr><td>${esc(r.country)}</td>
 <td>${esc(yearLabel(r.year))}</td>
 <td>${esc(metricLabels[r.metric]||r.metric)}</td>
 <td>${esc(fmt(r.value))}</td>
 <td>${esc(r.source)}</td>
 <td>${esc(r.dataset)}</td></tr>
 `).join("");
}
["primary","compare","metric","scale"].forEach(id=>
 $(id).addEventListener("change",()=>refresh(id))
);
["start","end"].forEach(id=>
 $(id).addEventListener("input",()=>refresh(id))
);
refresh();
</script>
</body>
</html>
"""

# Inline data also works when opening the HTML directly from Finder.
safe_json = json.dumps(records, ensure_ascii=False).replace("<", "\\u003c")
target = OUT / "economic_dashboard.html"
target.write_text(
    html.replace("__DATA__", safe_json),
    encoding="utf-8"
)

print("\nDashboard:", target)
print("Observations:", len(records))
print("Countries:", data["country"].nunique())
print("Available metrics:", sorted(data["metric"].unique().tolist()))
print("Year range:", data["year"].min(), "to", data["year"].max())
