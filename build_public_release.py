from pathlib import Path
from datetime import datetime, timezone
import json
import re
import shutil
import pandas as pd

ROOT = Path("reports/output")
PUBLIC = Path("reports/public")

YIELDS = Path("data/gold/macro/yield_spread.parquet")
UNEMP = Path("data/gold/macro/unemployment.parquet")

for path in [YIELDS, UNEMP]:
    if not path.exists():
        raise SystemExit(f"Missing FRED Gold dataset: {path}")

def load(path, columns):
    df = pd.read_parquet(path)
    missing = set(columns) - set(df.columns)
    if missing:
        raise SystemExit(f"{path} missing {sorted(missing)}")

    df = df[columns].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date").drop_duplicates("date", keep="last")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    for col in columns:
        if col != "date":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return json.loads(df.to_json(orient="records"))

yields = load(YIELDS, [
    "date", "yield_10y", "yield_3m", "yield_spread_10y_3m"
])
unemployment = load(UNEMP, ["date", "value"])

if not yields or not unemployment:
    raise SystemExit("Macro datasets must not be empty")

data = json.dumps(
    {"yields": yields, "unemployment": unemployment},
    ensure_ascii=False
).replace("<", "\\u003c")

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>US Macroeconomic Risk | Analytics Platform</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f5f7fb;color:#1b2940;font-family:system-ui,Arial}
header{background:#142741;color:white;padding:26px 5%}
header a{color:#cee1ff}
main{max-width:1250px;margin:auto;padding:24px}
.card{background:white;border:1px solid #dce4ef;border-radius:12px;padding:20px;min-width:0}
.filters,.kpis,.charts{display:grid;gap:15px}
.filters{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.kpis{grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin:20px 0}
.charts{grid-template-columns:repeat(auto-fit,minmax(390px,1fr))}
.wide{grid-column:1/-1}
label{display:block;font-size:13px;margin-bottom:6px}
input{width:100%;padding:10px;border:1px solid #ccd6e3;border-radius:7px}
button{background:#174c94;color:white;border:0;border-radius:7px;padding:11px 16px;cursor:pointer}
.value{font-size:26px;font-weight:700;margin:5px 0}
.muted{color:#66758b;font-size:13px}
.chart{height:370px}
.notice{background:#edf3fd;border-left:4px solid #4777db;padding:16px;border-radius:8px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;border-bottom:1px solid #e3e8f0;padding:10px}
th{background:#f0f4fa}
.tablewrap{overflow:auto;max-height:420px}
footer{text-align:center;padding:30px;color:#66758b;font-size:13px}
@media(max-width:650px){
 main{padding:12px}
 .charts{grid-template-columns:1fr}
 .chart{height:300px}
}
</style>
</head>
<body>
<header>
<a href="index.html#usecases">← Back to Use Cases</a>
<h1>US Macroeconomic Risk Explorer</h1>
<p>Interactive Treasury yield, yield curve, and labor market indicators.</p>
</header>
<main>
<div class="notice">
<strong>Public-data edition.</strong>
This dashboard presents Federal Reserve economic series.
SPY prices and Yahoo-derived market analytics are retained
outside this public publishing path. Equity metrics are
temporarily unavailable here pending a suitable data license.
</div>

<section class="card" style="margin-top:20px">
<h3>Time period</h3>
<div class="filters">
<div><label>Start date</label><input type="date" id="start"></div>
<div><label>End date</label><input type="date" id="end"></div>
<div style="align-self:end"><button id="reset">Reset range</button></div>
</div>
<p id="status" class="muted"></p>
</section>

<section class="kpis">
<div class="card"><div class="muted">10-year yield</div><div class="value" id="ten">—</div><div class="muted" id="tenDate"></div></div>
<div class="card"><div class="muted">3-month yield</div><div class="value" id="three">—</div><div class="muted" id="threeDate"></div></div>
<div class="card"><div class="muted">10Y–3M spread</div><div class="value" id="spread">—</div><div class="muted" id="spreadDate"></div></div>
<div class="card"><div class="muted">Unemployment</div><div class="value" id="unemployment">—</div><div class="muted" id="unemploymentDate"></div></div>
</section>

<section class="charts">
<div class="card wide">
<h3>Treasury yields</h3>
<div class="chart" id="yieldChart"></div>
</div>
<div class="card">
<h3>10Y–3M yield spread</h3>
<div class="chart" id="spreadChart"></div>
</div>
<div class="card">
<h3>Unemployment rate</h3>
<div class="chart" id="unemploymentChart"></div>
</div>
</section>

<section class="card" style="margin-top:20px">
<h3>Latest Treasury observations in selected range</h3>
<div class="tablewrap">
<table>
<thead><tr><th>Date</th><th>10Y (%)</th><th>3M (%)</th><th>Spread (pp)</th></tr></thead>
<tbody id="observations"></tbody>
</table>
</div>
</section>

<section class="card" style="margin-top:20px">
<h3>Sources and methodology</h3>
<p>Data: Federal Reserve Economic Data (FRED), Federal Reserve Bank of St. Louis.</p>
<p>
<a href="https://fred.stlouisfed.org/series/DGS10">DGS10</a>:
10-Year Treasury Constant Maturity Rate.
<a href="https://fred.stlouisfed.org/series/DGS3MO">DGS3MO</a>:
3-Month Treasury Constant Maturity Rate.
<a href="https://fred.stlouisfed.org/series/UNRATE">UNRATE</a>:
Civilian Unemployment Rate.
</p>
<p class="muted">
Treasury yields and unemployment are displayed in percent.
The yield spread is measured in percentage points.
Unemployment observations are monthly; Treasury observations
are daily. Values are not interpolated across missing dates.
The latest value in a selected range may have an earlier
observation date than other metrics.
</p>
<p class="muted">
This is descriptive analysis, not investment advice or
a validated recession-prediction model.
</p>
</section>
</main>
<footer>Analytics Platform · Public Macro Risk Edition</footer>

<script>
const DATA=__DATA__;
const $=id=>document.getElementById(id);
const yields=DATA.yields;
const unemployment=DATA.unemployment;
const config={responsive:true,displaylogo:false};

function valid(v){return v!==null&&v!==undefined&&Number.isFinite(Number(v));}
function latest(rows,key){
 for(let i=rows.length-1;i>=0;i--){
  if(valid(rows[i][key]))return rows[i];
 }
 return null;
}
function fmt(v,unit){
 return valid(v)?Number(v).toFixed(2)+unit:"—";
}
function filter(rows,start,end){
 return rows.filter(r=>r.date>=start&&r.date<=end);
}
function kpi(id,dateId,rows,key,unit){
 const row=latest(rows,key);
 $(id).textContent=row?fmt(row[key],unit):"—";
 $(dateId).textContent=row?"As of "+row.date:"No observations";
}
function trace(rows,key,name){
 return {
  type:"scatter",mode:"lines",name,
  x:rows.map(r=>r.date),
  y:rows.map(r=>valid(r[key])?Number(r[key]):null),
  connectgaps:false
 };
}
function chart(id,traces,title){
 Plotly.react(id,traces,{
  paper_bgcolor:"white",plot_bgcolor:"white",
  margin:{l:75,r:25,t:15,b:55},
  xaxis:{title:"Date",type:"date"},
  yaxis:{title},
  hovermode:"x unified",
  font:{family:"Arial",size:12}
 },config);
}
function update(){
 const start=$("start").value,end=$("end").value;
 if(start>end){
  $("status").textContent="Start date must not exceed end date.";
  return;
 }
 const y=filter(yields,start,end);
 const u=filter(unemployment,start,end);
 $("status").textContent=
  `${y.length} Treasury dates and ${u.length} monthly unemployment observations.`;

 kpi("ten","tenDate",y,"yield_10y","%");
 kpi("three","threeDate",y,"yield_3m","%");
 kpi("spread","spreadDate",y,"yield_spread_10y_3m"," pp");
 kpi("unemployment","unemploymentDate",u,"value","%");

 chart("yieldChart",[
  trace(y,"yield_10y","10-year Treasury"),
  trace(y,"yield_3m","3-month Treasury")
 ],"Yield (%)");
 chart("spreadChart",[
  trace(y,"yield_spread_10y_3m","10Y–3M spread")
 ],"Percentage points");
 chart("unemploymentChart",[
  trace(u,"value","Unemployment")
 ],"Unemployment (%)");

 $("observations").innerHTML=[...y].reverse().slice(0,200).map(r=>`
  <tr><td>${r.date}</td>
  <td>${fmt(r.yield_10y,"")}</td>
  <td>${fmt(r.yield_3m,"")}</td>
  <td>${fmt(r.yield_spread_10y_3m,"")}</td></tr>
 `).join("");
}
function reset(){
 const end=yields[yields.length-1].date;
 const d=new Date(end+"T12:00:00Z");
 d.setUTCDate(d.getUTCDate()-365*3);
 $("start").value=d.toISOString().slice(0,10);
 $("end").value=end;
 update();
}
["start","end"].forEach(id=>$(id).addEventListener("change",update));
$("reset").addEventListener("click",reset);
reset();
</script>
</body>
</html>'''

# Build the public directory from scratch on every run.
if PUBLIC.exists():
    shutil.rmtree(PUBLIC)
PUBLIC.mkdir(parents=True)

public_macro = html.replace("__DATA__", data)
(PUBLIC / "market_dashboard.html").write_text(
    public_macro, encoding="utf-8"
)
(PUBLIC / "market_risk.html").write_text(
    public_macro, encoding="utf-8"
)

# Only explicitly approved pages enter the publication directory.
approved_pages = [
    "index.html",
    "forecasts_dashboard.html",
    "forecasts_vs_facts.html",
    "decisions_dashboard.html",
    "decisions_vs_outcomes.html",
    "economic_dashboard.html",
    "economic_history.html",
]

for name in approved_pages:
    src = ROOT / name
    if not src.exists():
        raise SystemExit(f"Required public page not found: {src}")
    shutil.copy2(src, PUBLIC / name)

# Clarify the temporary change on the published homepage.
index = PUBLIC / "index.html"
homepage = index.read_text(encoding="utf-8")

homepage = homepage.replace(
    "SPY market trends, moving averages, volatility,",
    "Treasury yields, yield curve behavior,"
).replace(
    "drawdowns, Treasury yield spreads and unemployment",
    "and unemployment indicators"
).replace(
    "Financial Markets & Macro Risk",
    "Public Macroeconomic Risk"
).replace(
    "Market Risk Monitor",
    "Macroeconomic Risk Explorer"
)

index.write_text(homepage, encoding="utf-8")

# Include only local image assets actually referenced by the
# three non-market static research reports.
safe_reports = [
    "forecasts_vs_facts.html",
    "decisions_vs_outcomes.html",
    "economic_history.html",
]
for name in safe_reports:
    page = (PUBLIC / name).read_text(encoding="utf-8")
    refs = re.findall(r'''(?:src|href)=["'](assets/[^"'?#]+)''', page)
    for ref in refs:
        rel = Path(ref)
        if (
            rel.is_absolute()
            or ".." in rel.parts
            or not rel.parts
            or rel.parts[0] != "assets"
        ):
            raise SystemExit(f"Unsafe asset reference: {ref}")
        if re.search(r"spy|market|volatility|drawdown|risk", ref, re.I):
            raise SystemExit(f"Review suspicious report asset: {ref}")
        source = ROOT / rel
        if not source.is_file():
            raise SystemExit(f"Missing referenced asset: {source}")
        destination = PUBLIC / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

# Explicit guard: no SPY market artifact or cached Yahoo output
# may be shipped in this public publication directory.
for file in PUBLIC.rglob("*"):
    if not file.is_file():
        continue
    if file.suffix.lower() in {".parquet", ".csv", ".md"}:
        raise SystemExit(f"Unapproved data/document file: {file}")
    if re.search(r"spy|volatility|drawdown", file.name, re.I):
        raise SystemExit(f"Possible market-data asset: {file}")

market_html = (PUBLIC / "market_dashboard.html").read_text()
for forbidden in [
    "spy_metrics", "yfinance", "adj_close",
    "running_peak", '"volume"', '"close"'
]:
    if forbidden in market_html:
        raise SystemExit(f"Market publication guard failed: {forbidden}")

manifest = sorted(
    str(p.relative_to(PUBLIC))
    for p in PUBLIC.rglob("*") if p.is_file()
)
print("\nPublic release generated:")
for name in manifest:
    print(" ", name)
print("\nFRED yield observations:", len(yields))
print("FRED unemployment observations:", len(unemployment))
print("Yahoo-derived equity observations published: 0 in macro page")
