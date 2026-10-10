from pathlib import Path
import json

from analytics_platform.datasets.gold import (
    build_decisions_vs_outcomes_gold,
)

OUTPUT = Path("reports/output")
OUTPUT.mkdir(parents=True, exist_ok=True)

df = build_decisions_vs_outcomes_gold()
records = json.loads(df.to_json(orient="records", date_format="iso"))

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Debated Decisions vs Outcomes</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f5f7fb;color:#172338;font-family:system-ui,Arial}
header{background:#142741;color:white;padding:25px 5%}
header a{color:#c4dfff}
main{max-width:1450px;margin:auto;padding:24px}
.card{background:white;border:1px solid #dfe5ee;border-radius:12px;padding:17px;min-width:0}
.filters,.stats,.charts{display:grid;gap:15px}
.filters{grid-template-columns:repeat(auto-fit,minmax(175px,1fr))}
.stats{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));margin:20px 0}
.charts{grid-template-columns:repeat(auto-fit,minmax(410px,1fr))}
label{display:block;font-size:13px;margin-bottom:6px}
select,input{width:100%;padding:10px;border:1px solid #cbd3df;border-radius:7px;background:white}
.stat{font-size:27px;font-weight:700;margin-top:6px}
.muted{color:#627085;font-size:13px}
.chart{height:390px}
.wide{grid-column:1/-1}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:11px;text-align:left;border-bottom:1px solid #e4e8f0;vertical-align:top}
th{background:#f1f4f9}
footer{text-align:center;padding:25px;color:#687587;font-size:12px}
@media(max-width:600px){
 main{padding:12px}
 .charts{grid-template-columns:1fr}
 .chart{height:330px}
}
</style>
</head>
<body>
<header>
<a href="index.html">← Analytics Platform</a>
<h1>Debated Decisions vs Outcomes</h1>
<p>Compare historical policy expectations with observed evidence.</p>
</header>

<main>
<section class="card">
<h3>Explore decisions</h3>
<div class="filters">
<div><label>Policy category</label><select id="category"></select></div>
<div><label>Jurisdiction</label><select id="region"></select></div>
<div><label>Claim type</label><select id="type"></select></div>
<div><label>Confidence</label><select id="confidence"></select></div>
<div><label>Decision year</label><select id="year"></select></div>
<div><label>Search</label><input id="search" placeholder="Transport, alcohol, levy..."></div>
</div>
</section>

<section class="stats">
<div class="card"><div class="muted">Evidence records</div><div id="count" class="stat">—</div></div>
<div class="card"><div class="muted">Distinct decisions</div><div id="decisions" class="stat">—</div></div>
<div class="card"><div class="muted">Policy categories</div><div id="categories" class="stat">—</div></div>
<div class="card"><div class="muted">High-confidence records</div><div id="high" class="stat">—</div></div>
</section>

<section class="charts">
<div class="card">
<h3>Observed vs predicted index</h3>
<p class="muted">Published prediction = 100. Only comparable positive, numeric point claims are included.</p>
<div id="comparison" class="chart"></div>
</div>
<div class="card">
<h3>Decision-to-outcome horizon</h3>
<div id="timeline" class="chart"></div>
</div>
<div class="card wide">
<h3>Category × claim type</h3>
<p class="muted">Number of evidence records in each group; this is a coverage heatmap, not an accuracy score.</p>
<div id="heatmap" class="chart"></div>
</div>
</section>

<section class="card" style="margin-top:20px">
<h3>Decision evidence explorer</h3>
<p class="muted">Click the original and outcome sources. Observed results do not independently establish causation.</p>
<div class="tablewrap">
<table>
<thead><tr>
<th>Decision</th><th>Date</th><th>Claim type</th>
<th>Original claim</th><th>Observed outcome</th>
<th>Outcome date</th><th>Evidence / interpretation</th><th>Sources</th>
</tr></thead>
<tbody id="table"></tbody>
</table>
</div>
</section>
</main>

<footer>Analytics Platform · Evidence and interpretation remain separate</footer>

<script>
const DATA=__ROWS__;
const $=id=>document.getElementById(id);

function esc(v){
 return String(v??"—").replace(/[&<>"']/g,c=>({
  "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
 })[c]);
}
function date(v){return v?String(v).slice(0,10):"—";}
function num(v){
 if(v===null||v===undefined||v==="")return null;
 const n=Number(v);return Number.isFinite(n)?n:null;
}
function source(url,label){
 if(!/^https:\/\//i.test(url||""))return "—";
 return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
}
function options(id,values){
 const s=$(id);
 s.innerHTML="";

 const items=[
  "All",
  ...[...new Set(
   values.map(v=>String(v??"Unspecified"))
  )].filter(v=>v!=="All").sort()
 ];

 items.forEach(v=>{
  const o=document.createElement("option");
  o.value=v;
  o.textContent=v;
  s.appendChild(o);
 });
}
function year(r){return date(r.decision_date).slice(0,4);}
function title(r){return String(r.decision||"Unknown decision");}
options("category",DATA.map(r=>r.category));
options("region",DATA.map(r=>r.jurisdiction));
options("type",DATA.map(r=>r.claim_type));
options("confidence",DATA.map(r=>r.confidence));
options("year",DATA.map(year));

const config={responsive:true,displaylogo:false};
const base={
 paper_bgcolor:"white",plot_bgcolor:"white",
 font:{family:"Arial",size:12},
 margin:{l:85,r:25,t:20,b:85}
};
function emptyChart(id,message){
 Plotly.react(id,[],{...base,annotations:[{
  x:.5,y:.5,xref:"paper",yref:"paper",
  showarrow:false,text:message
 }]},config);
}
function matches(v,selection){
 return selection==="All"||String(v??"Unspecified")===selection;
}
function refresh(){
 const search=$("search").value.toLowerCase();
 const rows=DATA.filter(r=>
  matches(r.category,$("category").value)&&
  matches(r.jurisdiction,$("region").value)&&
  matches(r.claim_type,$("type").value)&&
  matches(r.confidence,$("confidence").value)&&
  matches(year(r),$("year").value)&&
  [r.decision,r.claim_at_time,r.category,r.predicted_metric]
   .some(v=>String(v||"").toLowerCase().includes(search))
 );

 $("count").textContent=rows.length;
 $("decisions").textContent=new Set(rows.map(title)).size;
 $("categories").textContent=new Set(rows.map(r=>r.category)).size;
 $("high").textContent=rows.filter(r=>r.confidence==="high").length;

 // Comparison index: equal numeric point estimates only.
 // Do not treat threshold or interval bounds as point forecasts.
 const comparable=rows.filter(r=>
  r.predicted_operator==="eq"&&
  num(r.predicted_value)!==null&&num(r.predicted_value)>0&&
  num(r.outcome_value)!==null&&
  r.predicted_metric===r.outcome_metric&&
  r.predicted_unit===r.outcome_unit
 );
 if(comparable.length){
  const labels=comparable.map(r=>r.decision_id);
  Plotly.react("comparison",[
   {type:"bar",name:"Published prediction",x:labels,y:comparable.map(()=>100)},
   {type:"bar",name:"Observed outcome",x:labels,
    y:comparable.map(r=>num(r.outcome_value)/num(r.predicted_value)*100),
    customdata:comparable.map(r=>r.decision+" — "+r.predicted_metric),
    hovertemplate:"%{customdata}<br>Index: %{y:.1f}<extra></extra>"}
  ],{...base,barmode:"group",
    yaxis:{title:"Index (prediction = 100)"},
    xaxis:{tickangle:-25,automargin:true}},config);
 }else emptyChart("comparison","No comparable point estimates for these filters");

 const horizons=rows.map(r=>({
  r,years:num(r.outcome_horizon_years)
 })).filter(x=>x.years!==null&&x.years>=0)
   .sort((a,b)=>a.years-b.years);
 if(horizons.length){
  Plotly.react("timeline",[{
   type:"bar",orientation:"h",
   y:horizons.map(x=>x.r.decision_id),
   x:horizons.map(x=>x.years),
   customdata:horizons.map(x=>title(x.r)),
   hovertemplate:"%{customdata}<br>%{x:.1f} years<extra></extra>"
  }],{...base,margin:{l:190,r:20,t:15,b:65},
    yaxis:{automargin:true},xaxis:{title:"Years to outcome"}},config);
 }else emptyChart("timeline","No horizon data");

 const cats=[...new Set(rows.map(r=>r.category||"Unspecified"))].sort();
 const types=[...new Set(rows.map(r=>r.claim_type||"Unspecified"))].sort();
 if(cats.length&&types.length){
  const matrix=cats.map(c=>types.map(t=>
   rows.filter(r=>(r.category||"Unspecified")===c&&
    (r.claim_type||"Unspecified")===t).length
  ));
  Plotly.react("heatmap",[{
   type:"heatmap",x:types,y:cats,z:matrix,colorscale:"Blues",
   text:matrix,texttemplate:"%{text}",
   hovertemplate:"%{y} · %{x}<br>%{z} records<extra></extra>"
  }],{...base,margin:{l:175,r:25,t:15,b:95}},config);
 }else emptyChart("heatmap","No records match");

 $("table").innerHTML=rows.map(r=>{
  const observed=num(r.outcome_value);
  return `<tr>
   <td><strong>${esc(r.decision)}</strong><div class="muted">${esc(r.jurisdiction)}</div></td>
   <td>${esc(date(r.decision_date))}</td>
   <td>${esc(r.claim_type)}</td>
   <td>${esc(r.claim_at_time)}</td>
   <td>${observed===null?"—":esc(observed)} ${esc(r.outcome_unit)}</td>
   <td>${esc(date(r.outcome_date))}</td>
   <td><strong>Evidence:</strong> ${esc(r.evidence_summary)}
     <p><strong>Interpretation:</strong> ${esc(r.interpretation)}</p></td>
   <td>${source(r.claim_url,"Claim")} · ${source(r.outcome_url,"Outcome")}</td>
  </tr>`;
 }).join("");
}
["category","region","type","confidence","year","search"].forEach(id=>
 $(id).addEventListener(id==="search"?"input":"change",refresh)
);
refresh();
</script>
</body>
</html>
"""

safe = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
html = html.replace("__ROWS__", safe)

path = OUTPUT / "decisions_dashboard.html"
path.write_text(html, encoding="utf-8")

print("Generated:", path)
print("Evidence records:", len(records))
