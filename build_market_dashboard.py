from pathlib import Path
import json
import pandas as pd

BASE = Path("data/gold")
OUT = Path("reports/output")
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "market": BASE / "market/spy_metrics.parquet",
    "yields": BASE / "macro/yield_spread.parquet",
    "unemployment": BASE / "macro/unemployment.parquet",
}

payload = {}

for name, path in SOURCES.items():
    if not path.exists():
        raise SystemExit(f"Missing dataset: {path}")

    df = pd.read_parquet(path).copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date").drop_duplicates("date", keep="last")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    if name == "market":
        columns = [
            "date", "close", "ma_200",
            "volatility_30d", "drawdown", "volume"
        ]
    elif name == "yields":
        columns = [
            "date", "yield_10y", "yield_3m",
            "yield_spread_10y_3m"
        ]
    else:
        columns = ["date", "value"]

    missing = set(columns) - set(df.columns)
    if missing:
        raise SystemExit(f"{path} missing columns: {sorted(missing)}")

    df = df[columns]

    for col in columns:
        if col != "date":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    payload[name] = json.loads(df.to_json(orient="records"))
    print(f"{name}: {len(df)} observations")

if not payload["market"]:
    raise SystemExit("SPY dataset is empty")

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Interactive Market Risk Explorer</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f5f7fb;color:#172338;font-family:system-ui,Arial}
header{background:#142741;color:white;padding:25px 5%}
header a{color:#c4dfff}
main{max-width:1450px;margin:auto;padding:24px}
.card{background:white;border:1px solid #e0e5ee;border-radius:12px;padding:18px;min-width:0}
.controls,.stats,.charts{display:grid;gap:15px}
.controls{grid-template-columns:repeat(auto-fit,minmax(185px,1fr))}
.stats{grid-template-columns:repeat(auto-fit,minmax(175px,1fr));margin:20px 0}
.charts{grid-template-columns:repeat(auto-fit,minmax(400px,1fr))}
.wide{grid-column:1/-1}
label{display:block;font-size:13px;margin-bottom:7px}
input,select{width:100%;padding:10px;border:1px solid #cbd3df;border-radius:7px;background:white}
button{padding:10px 17px;background:#142741;color:white;border:0;border-radius:7px;cursor:pointer}
.stat{font-size:25px;font-weight:700;margin-top:6px}
.muted{font-size:13px;color:#627087}
.chart{height:375px}
.wide .chart{height:420px}
.tablewrap{max-height:430px;overflow:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px;text-align:left;border-bottom:1px solid #e5e9f0}
th{position:sticky;top:0;background:#f1f4f9}
footer{text-align:center;color:#687789;padding:24px;font-size:12px}
@media(max-width:600px){
 main{padding:12px}
 .charts{grid-template-columns:1fr}
 .chart,.wide .chart{height:320px}
}
</style>
</head>
<body>
<header>
<a href="index.html">← Analytics Platform</a>
<h1>Interactive Market Risk Explorer</h1>
<p>SPY trends, volatility, drawdowns, and macroeconomic risk indicators.</p>
</header>

<main>
<section class="card">
<h3>Dashboard controls</h3>
<div class="controls">
<div><label>Start date</label><input type="date" id="start"></div>
<div><label>End date</label><input type="date" id="end"></div>
<div>
<label>Risk indicator</label>
<select id="risk">
<option value="volatility_30d">30-day volatility</option>
<option value="drawdown">Drawdown</option>
</select>
</div>
<div>
<label>Macro indicator</label>
<select id="macro">
<option value="yield_spread_10y_3m">10Y–3M yield spread</option>
<option value="yield_10y">10-year Treasury yield</option>
<option value="yield_3m">3-month Treasury yield</option>
<option value="unemployment">Unemployment rate</option>
</select>
</div>
<div style="align-self:end"><button id="reset">Reset filters</button></div>
</div>
<p id="windowInfo" class="muted"></p>
</section>

<section class="stats">
<div class="card"><div class="muted">Latest SPY close</div><div id="close" class="stat">—</div><div id="closeDate" class="muted"></div></div>
<div class="card"><div class="muted">30-day volatility</div><div id="vol" class="stat">—</div><div id="volDate" class="muted"></div></div>
<div class="card"><div class="muted">Latest drawdown</div><div id="dd" class="stat">—</div><div id="ddDate" class="muted"></div></div>
<div class="card"><div class="muted">10Y–3M spread</div><div id="spread" class="stat">—</div><div id="spreadDate" class="muted"></div></div>
<div class="card"><div class="muted">Unemployment</div><div id="unemp" class="stat">—</div><div id="unempDate" class="muted"></div></div>
</section>

<section class="charts">
<div class="card wide">
<h3>SPY price vs 200-day moving average</h3>
<div id="priceChart" class="chart"></div>
</div>
<div class="card">
<h3 id="riskTitle">Market risk</h3>
<div id="riskChart" class="chart"></div>
</div>
<div class="card">
<h3 id="macroTitle">Macroeconomic indicator</h3>
<div id="macroChart" class="chart"></div>
</div>
<div class="card wide">
<h3>SPY trading volume</h3>
<div id="volumeChart" class="chart"></div>
</div>
</section>

<section class="card" style="margin-top:20px">
<h3>Underlying market observations</h3>
<p class="muted">Latest 250 observations in the selected period. All figures are derived from the existing Gold datasets.</p>
<div class="tablewrap">
<table>
<thead>
<tr><th>Date</th><th>SPY close</th><th>200-day MA</th>
<th>30-day volatility</th><th>Drawdown</th><th>Volume</th></tr>
</thead>
<tbody id="table"></tbody>
</table>
</div>
</section>
</main>

<footer>Analytics Platform · Market data: Yahoo Finance · Macroeconomic data: FRED</footer>

<script>
const DATA=__DATA__;
const $=id=>document.getElementById(id);
const market=DATA.market;
const yields=DATA.yields;
const unemployment=DATA.unemployment;

const minDate=market[0].date;
const maxDate=market[market.length-1].date;

const config={responsive:true,displaylogo:false,scrollZoom:true};
const base={
 paper_bgcolor:"white",
 plot_bgcolor:"white",
 font:{family:"Arial",size:12},
 margin:{l:75,r:20,t:20,b:60},
 hovermode:"x unified",
 xaxis:{type:"date",automargin:true}
};

function fmt(v,d=2){
 return v==null||!Number.isFinite(Number(v))?"—":
 Number(v).toLocaleString("en-US",{
  minimumFractionDigits:d,maximumFractionDigits:d
 });
}

function range(arr,start,end){
 return arr.filter(r=>r.date>=start&&r.date<=end);
}

function lastValid(arr,key){
 for(let i=arr.length-1;i>=0;i--){
  if(arr[i][key]!==null&&arr[i][key]!==undefined&&
     Number.isFinite(Number(arr[i][key])))return arr[i];
 }
 return null;
}

function showKpi(id,dateId,rows,key,transform,suffix,prefix=""){
 const r=lastValid(rows,key);
 $(id).textContent=r?prefix+fmt(transform(r[key]))+suffix:"—";
 $(dateId).textContent=r?"As of "+r.date:"No observations in range";
}

function series(rows,key,name,transform,type="scatter"){
 return {
  type,
  mode:type==="scatter"?"lines":undefined,
  name,
  x:rows.map(r=>r.date),
  y:rows.map(r=>r[key]==null?null:transform(r[key])),
  connectgaps:false,
  hovertemplate:"%{x}<br>"+name+": %{y:,.2f}<extra></extra>"
 };
}

function plot(id,traces,ytitle,extra={}){
 Plotly.react(id,traces,{
  ...base,
  yaxis:{title:ytitle,automargin:true},
  ...extra
 },config);
}

function refresh(){
 const start=$("start").value;
 const end=$("end").value;

 if(!start||!end||start>end){
  $("windowInfo").textContent="Choose a valid date range (start must not exceed end).";
  return;
 }

 const m=range(market,start,end);
 const y=range(yields,start,end);
 const u=range(unemployment,start,end);

 $("windowInfo").textContent=
  m.length+" market observations · "+
  y.length+" Treasury observations · "+
  u.length+" monthly unemployment observations";

 showKpi("close","closeDate",m,"close",v=>v,"$","");
 showKpi("vol","volDate",m,"volatility_30d",v=>v*100,"%");
 showKpi("dd","ddDate",m,"drawdown",v=>v*100,"%");
 showKpi("spread","spreadDate",y,"yield_spread_10y_3m",v=>v," pp");
 showKpi("unemp","unempDate",u,"value",v=>v,"%");

 plot("priceChart",[
  series(m,"close","SPY close",v=>v),
  series(m,"ma_200","200-day MA",v=>v)
 ],"USD");

 const risk=$("risk").value;
 const riskIsVol=risk==="volatility_30d";
 const riskLabel=riskIsVol?"30-day volatility":"Drawdown";
 $("riskTitle").textContent=riskLabel;
 plot("riskChart",[
  series(m,risk,riskLabel,v=>v*100)
 ],riskLabel+" (%)");

 const macro=$("macro").value;
 const macroInfo={
  yield_spread_10y_3m:["10Y–3M yield spread","Percentage points"],
  yield_10y:["10-year Treasury yield","Percent"],
  yield_3m:["3-month Treasury yield","Percent"],
  unemployment:["Unemployment rate","Percent"]
 };
 const info=macroInfo[macro];
 $("macroTitle").textContent=info[0];

 const macroRows=macro==="unemployment"?u:y;
 const macroKey=macro==="unemployment"?"value":macro;

 plot("macroChart",[
  series(macroRows,macroKey,info[0],v=>v)
 ],info[1],{xaxis:{type:"date",range:[start,end]}});

 plot("volumeChart",[
  series(m,"volume","SPY trading volume",v=>v,"bar")
 ],"Shares");

 const recent=[...m].reverse().slice(0,250);
 $("table").innerHTML=recent.map(r=>`
 <tr>
 <td>${r.date}</td>
 <td>${fmt(r.close)}</td>
 <td>${fmt(r.ma_200)}</td>
 <td>${r.volatility_30d==null?"—":fmt(r.volatility_30d*100)+"%"}</td>
 <td>${r.drawdown==null?"—":fmt(r.drawdown*100)+"%"}</td>
 <td>${fmt(r.volume,0)}</td>
 </tr>
 `).join("");
}

$("start").min=minDate;
$("start").max=maxDate;
$("end").min=minDate;
$("end").max=maxDate;

function reset(){
 // Initial view: latest 365 calendar days.
 const d=new Date(maxDate+"T12:00:00Z");
 d.setUTCDate(d.getUTCDate()-365);
 const defaultStart=d.toISOString().slice(0,10);
 $("start").value=defaultStart<minDate?minDate:defaultStart;
 $("end").value=maxDate;
 $("risk").value="volatility_30d";
 $("macro").value="yield_spread_10y_3m";
 refresh();
}

["start","end","risk","macro"].forEach(id=>
 $(id).addEventListener("change",refresh)
);
$("reset").addEventListener("click",reset);

reset();
</script>
</body>
</html>
"""

safe = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
target = OUT / "market_dashboard.html"
target.write_text(html.replace("__DATA__", safe), encoding="utf-8")

print("\nGenerated:", target)
print("SPY dates:", payload["market"][0]["date"],
      "to", payload["market"][-1]["date"])
print("HTML size:", round(target.stat().st_size / 1024), "KB")
