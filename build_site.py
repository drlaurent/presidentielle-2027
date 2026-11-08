#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a polished, self-contained web map for GitHub/Vercel."""
from pathlib import Path
import json
import requests
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

geo = gpd.read_file(DATA / "projection-departementale.geojson").to_crs(4326)
geo["code_departement"] = geo["code_departement"].astype(str).str.zfill(2)
geojson = json.loads(geo.to_json())
intentions = pd.read_csv(DATA / "intentions-vote-vague-reference.csv", sep=";", decimal=",", encoding="utf-8-sig")
intentions_json = intentions[["candidat", "parti", "intentions_vote_pct", "date_publication", "institut"]].to_dict("records")

leaflet_js = requests.get("https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js", timeout=30).text
leaflet_css = requests.get("https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css", timeout=30).text

html = r'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Présidentielle 2027 — projections départementales</title>
<style>__LEAFLET_CSS__</style>
<style>
:root{--ink:#172033;--muted:#697386;--line:#e5e9f0;--paper:#fff;--bg:#f3f5f8;--accent:#2447c6;--shadow:0 14px 40px #17203314}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow:hidden}
#app{height:100vh;display:grid;grid-template-columns:360px 1fr;grid-template-rows:1fr}
#panel{background:var(--paper);border-right:1px solid var(--line);padding:25px 24px;overflow:auto;z-index:10}
.brand{display:flex;gap:12px;align-items:center;margin-bottom:24px}.mark{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#2447c6,#6e81e6);color:#fff;display:grid;place-items:center;font-weight:800;font-size:18px}.eyebrow{text-transform:uppercase;letter-spacing:.12em;color:var(--accent);font-weight:800;font-size:10px}.brand h1{font-size:18px;line-height:1.1;margin:3px 0 0}.brand p{color:var(--muted);margin:2px 0 0;font-size:12px}
.section{border-top:1px solid var(--line);padding-top:18px;margin-top:18px}.section h2{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 10px}
.segmented{display:grid;grid-template-columns:1fr 1fr;background:#eef1f6;border-radius:10px;padding:3px}.segmented button{border:0;background:transparent;border-radius:8px;padding:9px 5px;color:var(--muted);font-weight:750;cursor:pointer}.segmented button.active{background:#fff;color:var(--ink);box-shadow:0 2px 8px #17203318}
select{width:100%;border:1px solid #dce2eb;background:#fff;border-radius:9px;padding:11px 12px;font:inherit;color:var(--ink);outline:none}select:focus{border-color:var(--accent);box-shadow:0 0 0 3px #2447c61c}
.score-card{display:flex;justify-content:space-between;align-items:end;padding:15px;border:1px solid var(--line);border-radius:12px;margin-top:12px;background:linear-gradient(145deg,#fff,#f8faff)}.score-card .name{font-weight:800}.score-card .party{color:var(--muted);font-size:12px}.score-card strong{font-size:28px;letter-spacing:-.04em}.score-card small{color:var(--muted);font-size:11px}
.meta{display:grid;grid-template-columns:1fr 1fr;gap:8px}.meta div{background:#f7f8fb;border-radius:9px;padding:10px}.meta b{display:block;font-size:16px}.meta span{color:var(--muted);font-size:11px}
.note{font-size:12px;color:var(--muted);background:#f7f8fb;border-radius:10px;padding:12px}.note b{color:var(--ink)}
#map{height:100%;min-height:500px;background:#dfe7f1;position:relative}.leaflet-container{background:#dfe7f1}.leaflet-control-zoom{border:0!important;box-shadow:var(--shadow)!important}.leaflet-control-zoom a{color:var(--ink)!important;border:0!important}
#map-head{position:absolute;left:24px;right:24px;top:20px;z-index:500;display:flex;justify-content:space-between;pointer-events:none}.pill{background:#fffffff2;border:1px solid #fff;border-radius:999px;padding:9px 14px;box-shadow:var(--shadow);font-weight:750}.pill span{color:var(--muted);font-weight:500;margin-left:6px}
#legend{position:absolute;bottom:25px;right:24px;z-index:500;background:#fffffff5;padding:12px 14px;border-radius:12px;box-shadow:var(--shadow);min-width:180px}.legend-title{font-weight:800;margin-bottom:6px}.gradient{height:9px;border-radius:9px;background:linear-gradient(90deg,#edf1fb,var(--legend));margin:4px 0}.legend-labels{display:flex;justify-content:space-between;color:var(--muted);font-size:11px}
#detail{position:absolute;bottom:24px;left:24px;z-index:500;background:#fffffff5;border-radius:12px;padding:13px 15px;box-shadow:var(--shadow);min-width:230px;display:none}.detail-name{font-size:16px;font-weight:850}.detail-row{display:flex;justify-content:space-between;gap:20px;color:var(--muted);margin-top:4px}.detail-row b{color:var(--ink)}
.source{font-size:11px;color:var(--muted);margin-top:15px}.source a{color:var(--accent)}
@media(max-width:800px){body{overflow:auto}#app{display:block;height:auto;min-height:100vh}#panel{border-right:0;padding:18px;max-height:none}#map{height:70vh;min-height:520px}#map-head{left:12px;right:12px;top:12px}.pill{font-size:12px;padding:7px 10px}#legend{right:12px;bottom:12px}#detail{left:12px;bottom:12px}}
</style>
</head>
<body>
<div id="app">
<aside id="panel">
  <div class="brand"><div class="mark">27</div><div><div class="eyebrow">Projection électorale</div><h1>Présidentielle 2027</h1><p>Lecture départementale des sondages</p></div></div>
  <div class="section" style="border-top:0;padding-top:0;margin-top:0"><h2>Scénario</h2><div class="segmented"><button id="t1" class="active">1er tour</button><button id="t2">2nd tour</button></div></div>
  <div class="section"><h2 id="choice-label">Candidat à afficher</h2><select id="choice"></select></div>
  <div id="score"></div>
  <div class="section"><h2>Repères nationaux</h2><div class="meta"><div><b id="date">—</b><span>date du sondage</span></div><div><b id="institute">—</b><span>institut</span></div></div><div id="national" style="margin-top:10px"></div></div>
  <div class="section"><h2>À lire avant d'interpréter</h2><div class="note"><b>Projection, pas résultat.</b><br>La carte reprend uniquement les projections départementales présentes dans la source. Les autres candidats peuvent être mesurés au niveau national sans disposer d'une projection locale.</div></div>
  <div class="source">Source : <a href="https://www.data.gouv.fr/datasets/presidentielle-2027-sondages-candidatures-et-projection-departementale" target="_blank">Repère 2027 / data.gouv.fr</a><br>Carte autonome — données embarquées dans cette page.</div>
</aside>
<main id="map"><div id="map-head"><div class="pill" id="map-title">1er tour <span>Marine Le Pen</span></div><div class="pill">96 départements</div></div><div id="legend"><div class="legend-title">Score projeté</div><div class="gradient"></div><div class="legend-labels"><span id="min">0 %</span><span id="max">50 %</span></div></div><div id="detail"></div></main>
</div>
<script>__LEAFLET_JS__</script>
<script>
const GEOJSON=__GEOJSON__;
const NATIONAL=__NATIONAL__;
const T1=[
 {label:'Marine Le Pen', field:'t1_marine_le_pen_pct', color:'#d23b50', party:'RN'},
 {label:'Édouard Philippe', field:'t1_edouard_philippe_pct', color:'#3564d4', party:'Horizons'},
 {label:'Jean-Luc Mélenchon', field:'t1_jean_luc_melenchon_pct', color:'#e58b28', party:'LFI'}
];
const T2=[
 {label:'Le Pen / Philippe', fields:['t2_duel1_m_le_pen_pct','t2_duel1_e_philippe_pct'], names:['Marine Le Pen','Édouard Philippe'], winner:'t2_duel1_vainqueur_estime', color:'#7445a8'},
 {label:'Le Pen / Glucksmann', fields:['t2_duel2_m_le_pen_pct','t2_duel2_r_glucksmann_pct'], names:['Marine Le Pen','Raphaël Glucksmann'], winner:'t2_duel2_vainqueur_estime', color:'#1c8b70'},
 {label:'Le Pen / Mélenchon', fields:['t2_duel3_m_le_pen_pct','t2_duel3_j_l_melenchon_pct'], names:['Marine Le Pen','Jean-Luc Mélenchon'], winner:'t2_duel3_vainqueur_estime', color:'#bd437e'}
];
let mode='t1', selected=T1[0], layer;
const $=id=>document.getElementById(id);
const fmt=n=>Number(n).toLocaleString('fr-FR',{minimumFractionDigits:1,maximumFractionDigits:1})+' %';
function rgb(hex){return hex.match(/\w\w/g).map(x=>parseInt(x,16))}
function shade(hex,value,min,max){let c=rgb(hex), t=Math.max(.08,Math.min(1,(value-min)/(max-min||1))), w=245; return `rgb(${c.map(x=>Math.round(w+(x-w)*t)).join(',')})`}
function values(){return GEOJSON.features.flatMap(f=>mode==='t1'?[Number(f.properties[selected.field])]:selected.fields.map(x=>Number(f.properties[x]))).filter(Number.isFinite)}
function updateSelect(){let list=mode==='t1'?T1:T2; $('choice').innerHTML=list.map((x,i)=>`<option value="${i}">${x.label}</option>`).join(''); selected=list[0]; render()}
function render(){let vals=values(), min=Math.min(...vals), max=Math.max(...vals); $('min').textContent=fmt(min);$('max').textContent=fmt(max);$('legend').style.setProperty('--legend',selected.color);$('map-title').innerHTML=(mode==='t1'?'1er tour':'2nd tour')+` <span>${selected.label}</span>`;
 const national=mode==='t1'?NATIONAL.find(x=>x.candidat===selected.label):null;
 $('score').innerHTML=mode==='t1'&&national?`<div class="score-card"><div><div class="name">${national.candidat}</div><div class="party">${national.parti}</div></div><div style="text-align:right"><strong>${fmt(national.intentions_vote_pct).replace(' %','')}</strong><small> % national</small></div></div>`:`<div class="score-card"><div><div class="name">${selected.label}</div><div class="party">Projection du duel</div></div><div style="text-align:right"><strong>3</strong><small> scénarios</small></div></div>`;
 $('date').textContent=NATIONAL[0]?.date_publication?.split(' ').slice(0,3).join(' ')||'—';$('institute').textContent=NATIONAL[0]?.institut||'—';
 $('national').innerHTML=mode==='t1'?NATIONAL.slice(0,6).map(x=>`<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #eef0f4"><span>${x.candidat}</span><b>${fmt(x.intentions_vote_pct)}</b></div>`).join(''):'<div class="note">Les scénarios nationaux du second tour sont affichés par département dans la carte.</div>';
 if(layer)layer.remove(); layer=L.geoJSON(GEOJSON,{style:f=>{let p=f.properties,v=mode==='t1'?Number(p[selected.field]):Number(p[selected.fields[0]]);return {fillColor:shade(selected.color,v,min,max),color:'#fff',weight:1,fillOpacity:.9}},onEachFeature:(f,l)=>{l.on({mouseover:e=>{e.target.setStyle({weight:3,color:'#172033'});showDetail(f.properties)},mouseout:e=>{layer.resetStyle(e.target)},click:e=>showDetail(f.properties)});}}).addTo(map); map.fitBounds(layer.getBounds(),{padding:[35,35]});}
function showDetail(p){let rows=mode==='t1'?[`${selected.label}|${fmt(p[selected.field])}`,`Candidat en tête|${p.t1_candidat_en_tete}`]:selected.fields.map((f,i)=>`${selected.names[i]}|${fmt(p[f])}`);$('detail').innerHTML=`<div class="detail-name">${p.departement}</div>${rows.map(x=>{let [a,b]=x.split('|');return `<div class="detail-row"><span>${a}</span><b>${b}</b></div>`}).join('')}`;$('detail').style.display='block'}
$('choice').addEventListener('change',e=>{selected=(mode==='t1'?T1:T2)[Number(e.target.value)];render()});$('t1').onclick=()=>{mode='t1';$('t1').classList.add('active');$('t2').classList.remove('active');$('choice-label').textContent='Candidat à afficher';updateSelect()};$('t2').onclick=()=>{mode='t2';$('t2').classList.add('active');$('t1').classList.remove('active');$('choice-label').textContent='Duel à afficher';updateSelect()};
const map=L.map('map',{zoomControl:true,attributionControl:false,scrollWheelZoom:true});updateSelect();
</script></body></html>'''

html = html.replace('__LEAFLET_CSS__', leaflet_css).replace('__LEAFLET_JS__', leaflet_js)
html = html.replace('__GEOJSON__', json.dumps(geojson, ensure_ascii=False, separators=(',',':')))
html = html.replace('__NATIONAL__', json.dumps(intentions_json, ensure_ascii=False, separators=(',',':')))
out = SITE / 'index.html'
out.write_text(html, encoding='utf-8')
# Copie à la racine pour un déploiement Vercel sans configuration de dossier.
root_out = ROOT / 'index.html'
root_out.write_text(html, encoding='utf-8')
print(f'[OK] {out} — {out.stat().st_size:,} octets — {len(geojson["features"])} départements')
print(f'[OK] {root_out} — copie Vercel')
