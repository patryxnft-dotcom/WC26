#!/usr/bin/env python3
"""Builds index.html from predictions.json + track_record.json (run from repo root)."""
import json, os
data = json.load(open('predictions.json'))
track = json.load(open('track_record.json')) if os.path.exists('track_record.json') else []
data['track'] = track[::-1]  # newest first

ISO = {'Mexico':'MX','South Africa':'ZA','South Korea':'KR','Czech Republic':'CZ','Canada':'CA',
'Bosnia and Herzegovina':'BA','Qatar':'QA','Switzerland':'CH','Brazil':'BR','Morocco':'MA','Haiti':'HT',
'United States':'US','Paraguay':'PY','Australia':'AU','Turkey':'TR','Germany':'DE','Curaçao':'CW',
'Ivory Coast':'CI','Ecuador':'EC','Netherlands':'NL','Japan':'JP','Sweden':'SE','Tunisia':'TN',
'Belgium':'BE','Egypt':'EG','Iran':'IR','New Zealand':'NZ','Spain':'ES','Cape Verde':'CV',
'Saudi Arabia':'SA','Uruguay':'UY','France':'FR','Senegal':'SN','Iraq':'IQ','Norway':'NO',
'Argentina':'AR','Algeria':'DZ','Austria':'AT','Jordan':'JO','Portugal':'PT','DR Congo':'CD',
'Uzbekistan':'UZ','Colombia':'CO','Croatia':'HR','Ghana':'GH','Panama':'PA'}
def flag(team):
    if team == 'England': return '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F'
    if team == 'Scotland': return '\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F'
    c = ISO.get(team)
    return (chr(0x1F1E6 + ord(c[0]) - 65) + chr(0x1F1E6 + ord(c[1]) - 65)) if c else '⚽'
data['flags'] = {t['team']: flag(t['team']) for t in data['power']}
DATA_JS = json.dumps(data, ensure_ascii=False)
rec = data.get('record', {'correct': 0, 'total': 0})
REC_CHIP = (f'<span class="chip"><b>{rec["correct"]}/{rec["total"]}</b> correct so far ({rec["correct"]/rec["total"]*100:.0f}%)</span>'
            if rec['total'] > 0 else '<span class="chip">Track record: <b>live from day 1</b></span>')

html = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GoldenBoot | World Cup 2026 Predictions, Powered by Data</title>
<meta name="description" content="Data-driven match predictions, group forecasts and champion odds for the FIFA World Cup 2026. Elo + Poisson model, backtested. Fair odds for every match.">
<meta property="og:title" content="GoldenBoot | World Cup 2026 Predictions">
<meta property="og:description" content="Probabilities for all 104 matches. Transparent model, public track record.">
<meta name="theme-color" content="#D4A843">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='80' font-size='80'>⚽</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0c10;--card:#13161d;--card2:#181c25;--line:#242a36;--txt:#eef1f6;--mut:#98a2b3;
--gold:#D4A843;--gold2:#e6c068;--blue:#5b7fa6;--slate:#3a4150;--grn:#4ade80;--red:#f87171;--rad:14px}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:'Inter',-apple-system,Segoe UI,sans-serif;font-size:15px;line-height:1.55}
a{color:var(--gold);text-decoration:none}
.wrap{max-width:1040px;margin:0 auto;padding:0 18px}
.hero{padding:44px 0 30px;text-align:center;background:radial-gradient(ellipse 70% 90% at 50% -20%,rgba(212,168,67,.13),transparent)}
.logo{font-weight:800;font-size:20px;margin-bottom:26px}.logo b{color:var(--gold)}
.hero h1{font-size:clamp(26px,4.5vw,40px);font-weight:800;letter-spacing:-.5px;line-height:1.15}
.hero h1 em{color:var(--gold);font-style:normal}
.hero p{color:var(--mut);max-width:560px;margin:14px auto 0;font-size:16px}
.chips{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:22px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:7px 16px;font-size:13px;color:var(--mut)}
.chip b{color:var(--txt)}
nav{position:sticky;top:0;z-index:10;background:rgba(10,12,16,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.tabs{display:flex;gap:6px;justify-content:center;padding:12px 10px;flex-wrap:wrap}
.tabs button{background:transparent;color:var(--mut);border:1px solid transparent;padding:8px 18px;border-radius:999px;cursor:pointer;font-size:14px;font-weight:600;font-family:inherit;transition:.15s}
.tabs button:hover{color:var(--txt)}.tabs button.on{background:var(--gold);color:#14130b}
main{padding:26px 0 10px;min-height:60vh}
.days{display:flex;gap:8px;overflow-x:auto;padding:2px 2px 14px;scrollbar-width:none}
.days::-webkit-scrollbar{display:none}
.days button{flex:0 0 auto;background:var(--card);border:1px solid var(--line);color:var(--mut);border-radius:10px;padding:8px 14px;cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;line-height:1.3}
.days button small{display:block;font-weight:500;font-size:11px}
.days button.on{border-color:var(--gold);color:var(--gold);background:rgba(212,168,67,.08)}
.m{background:var(--card);border:1px solid var(--line);border-radius:var(--rad);padding:18px;margin-bottom:12px;cursor:pointer;transition:border-color .15s}
.m:hover{border-color:#33394a}
.mtop{display:flex;align-items:center;justify-content:space-between;gap:8px}
.mteams{display:flex;align-items:center;gap:10px;font-weight:700;font-size:17px;flex-wrap:wrap}
.mteams .fl{font-size:22px}.vs{color:var(--mut);font-weight:500;font-size:13px}
.mmeta{color:var(--mut);font-size:12px;text-align:right;white-space:nowrap}
.gtag{display:inline-block;background:var(--card2);border:1px solid var(--line);border-radius:6px;padding:1px 8px;font-size:11px;color:var(--gold);font-weight:600;margin-left:6px}
.bar{display:flex;height:30px;border-radius:9px;overflow:hidden;margin-top:14px;font-size:12px;font-weight:700}
.bar div{display:flex;align-items:center;justify-content:center;min-width:40px;color:#0d0f08}
.s1{background:var(--gold)}.sx{background:var(--slate);color:var(--mut)!important}.s2{background:var(--blue);color:#0c1117!important}
.blabels{display:flex;justify-content:space-between;color:var(--mut);font-size:11.5px;margin-top:5px}
.mx{max-height:0;overflow:hidden;transition:max-height .25s ease}
.m.open .mx{max-height:280px}
.mxin{border-top:1px solid var(--line);margin-top:14px;padding-top:13px;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.stat{background:var(--card2);border-radius:10px;padding:10px 12px}
.stat .k{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.4px}
.stat .v{font-weight:700;font-size:15px;margin-top:2px}
.fair{grid-column:1/-1;color:var(--mut);font-size:12px}.fair b{color:var(--gold)}
.hint{text-align:center;color:var(--mut);font-size:12px;margin:4px 0 14px}
.ggrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
.g{background:var(--card);border:1px solid var(--line);border-radius:var(--rad);padding:16px}
.g h3{font-size:15px;color:var(--gold);margin-bottom:10px}
.g table{width:100%;border-collapse:collapse;font-size:13.5px}
.g td,.g th{padding:6px 4px;text-align:left;border-bottom:1px solid var(--line)}
.g th{color:var(--mut);font-size:11px;text-transform:uppercase;font-weight:600}
.g tr:last-child td{border-bottom:none}
.pb{background:var(--line);border-radius:4px;height:7px;width:64px;display:inline-block;vertical-align:middle;margin-right:7px}
.pb i{display:block;height:7px;border-radius:4px;background:var(--gold)}
.tbl{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:var(--rad);overflow:hidden}
.tbl th,.tbl td{padding:11px 16px;border-bottom:1px solid var(--line);text-align:left}
.tbl th{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.4px}
.tbl tr:last-child td{border-bottom:none}.tbl tr:hover td{background:var(--card2)}
.rank{color:var(--mut);width:40px}
.ok{color:var(--grn);font-weight:700}.bad{color:var(--red);font-weight:700}
.note{color:var(--mut);font-size:12.5px;margin-top:12px}
footer{border-top:1px solid var(--line);margin-top:44px;padding:26px 18px;text-align:center;color:var(--mut);font-size:12.5px}
footer .rg{margin-top:8px}
@media(max-width:560px){.mmeta{display:none}.bar{height:26px}}
</style></head><body>
<div class="hero"><div class="wrap">
<div class="logo">Golden<b>Boot</b> ⚽</div>
<h1>World Cup 2026 predictions,<br><em>powered by data</em>, not gut feeling</h1>
<p>An Elo + Poisson model trained on 49,000+ internationals since 1872. Every probability is transparent, backtested, and tracked publicly.</p>
<div class="chips">
<span class="chip"><b>104</b> matches covered</span>
<span class="chip"><b>10,000</b> tournament simulations</span>
__REC__
<span class="chip">Updated <b>daily</b></span>
</div>
</div></div>
<nav><div class="tabs">
<button class="on" data-v="matches">⚽ Matches</button>
<button data-v="groups">🏆 Groups</button>
<button data-v="record">📋 Track Record</button>
<button data-v="power">📊 Power Rankings</button>
<button data-v="champ">👑 Champion Odds</button>
</div></nav>
<main><div class="wrap" id="main"></div></main>
<footer>
GoldenBoot is an analytics project. Probabilities are model estimates, not guarantees. Short tournaments are high variance.
<div class="rg">18+ · Please gamble responsibly · <a href="https://www.begambleaware.org">BeGambleAware.org</a> · No betting operator affiliation.</div>
</footer>
<script>
const D = __DATA__;
const FL = D.flags;
const pct = p => Math.round(p*100)+'%';
const odds = p => (1/p).toFixed(2);
const fmtDay = d => new Date(d+'T12:00').toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short'});
let selDay = null;
function vMatches(){
  const days = [...new Set(D.matches.map(m=>m.date))];
  if(!days.length) return '<p class="note">No upcoming matches - tournament finished. Thanks for following!</p>';
  const today = new Date().toISOString().slice(0,10);
  if(!selDay || !days.includes(selDay)) selDay = days.includes(today) ? today : days.find(d=>d>=today) || days[0];
  let h = '<div class="days">' + days.map(d=>
    `<button class="${d===selDay?'on':''}" onclick="event.stopPropagation();selDay='${d}';show('matches')">${fmtDay(d).split(',')[0]}<small>${new Date(d+'T12:00').toLocaleDateString('en-GB',{day:'numeric',month:'short'})}</small></button>`).join('') + '</div>';
  h += '<div class="hint">Tap a match for likely scores, BTTS and fair odds</div>';
  for(const m of D.matches.filter(m=>m.date===selDay)){
    const best = m.top_scores.map(s=>`${s[0]} <span style="color:var(--mut)">(${pct(s[1])})</span>`).join(' · ');
    const tag = m.group==='KO' ? 'Knockout' : 'Group '+m.group;
    h += `<div class="m" onclick="this.classList.toggle('open')">
      <div class="mtop">
        <div class="mteams"><span class="fl">${FL[m.home]||''}</span>${m.home}<span class="vs">vs</span><span class="fl">${FL[m.away]||''}</span>${m.away}</div>
        <div class="mmeta">${m.city}<span class="gtag">${tag}</span></div>
      </div>
      <div class="bar">
        <div class="s1" style="flex:${m.p_home}">${pct(m.p_home)}</div>
        <div class="sx" style="flex:${m.p_draw}">${pct(m.p_draw)}</div>
        <div class="s2" style="flex:${m.p_away}">${pct(m.p_away)}</div>
      </div>
      <div class="blabels"><span>${m.home} win</span><span>draw</span><span>${m.away} win</span></div>
      <div class="mx"><div class="mxin">
        <div class="stat"><div class="k">Expected goals</div><div class="v">${m.xg_h} - ${m.xg_a}</div></div>
        <div class="stat"><div class="k">Over 2.5 goals</div><div class="v">${pct(m.over25)}</div></div>
        <div class="stat"><div class="k">Both teams score</div><div class="v">${pct(m.btts)}</div></div>
        <div class="stat"><div class="k">Likely scores</div><div class="v" style="font-size:13px">${best}</div></div>
        <div class="fair">Fair odds (1/p): <b>${odds(m.p_home)}</b> home · <b>${odds(m.p_draw)}</b> draw · <b>${odds(m.p_away)}</b> away A bookmaker price <i>above</i> these suggests value.</div>
      </div></div>
    </div>`;
  }
  return h;
}
function vGroups(){
  let h = '<div class="ggrid">';
  for(const g of Object.keys(D.groups)){
    h += `<div class="g"><h3>Group ${g}</h3><table><tr><th>Team</th><th>Pts</th><th>Advance</th></tr>`;
    for(const t of D.groups[g]){
      h += `<tr><td>${FL[t.team]||''} ${t.team}</td><td style="color:var(--mut)">${t.pts??0}</td>
      <td><span class="pb"><i style="width:${t.p_advance*100}%"></i></span>${pct(t.p_advance)}</td></tr>`;
    }
    h += '</table></div>';
  }
  return h + '</div><p class="note">"Advance" = probability of reaching the round of 32 (top 2 + 8 best third-placed teams). Played results are baked in; remaining matches are simulated 10,000 times.</p>';
}
function vRecord(){
  if(!D.track.length) return '<p class="note">No completed matches evaluated yet - the record goes live after the first matchday. Every prediction is locked in before kickoff and never edited.</p>';
  const n = D.track.length, c = D.track.filter(t=>t.correct).length;
  let h = `<p class="note" style="margin-bottom:12px">Every 1X2 pick the model made, locked before kickoff: <b style="color:var(--txt)">${c}/${n} correct (${Math.round(c/n*100)}%)</b></p>`;
  h += '<table class="tbl"><tr><th>Date</th><th>Match</th><th>Score</th><th>Pick (prob)</th><th>Result</th></tr>';
  for(const t of D.track){
    h += `<tr><td style="color:var(--mut)">${t.date.slice(5)}</td>
    <td>${FL[t.home]||''} ${t.home} - ${t.away} ${FL[t.away]||''}</td><td>${t.score}</td>
    <td>${t.pick} (${pct(t.pick_p)})</td>
    <td class="${t.correct?'ok':'bad'}">${t.correct?'✓ hit':'✗ miss'}</td></tr>`;
  }
  return h + '</table>';
}
function vPower(){
  let h = '<table class="tbl"><tr><th class="rank">#</th><th>Team</th><th>Elo rating</th></tr>';
  D.power.forEach((t,i)=>{h+=`<tr><td class="rank">${i+1}</td><td>${FL[t.team]||''} ${t.team}</td><td>${t.elo}</td></tr>`});
  return h + '</table><p class="note">Elo ratings over the full history of internationals, weighted by competition importance and margin of victory. Updates after every matchday.</p>';
}
function vChamp(){
  let h = '<table class="tbl"><tr><th>Team</th><th>Win probability</th><th>Fair odds</th></tr>';
  for(const c of D.champion){
    h += `<tr><td>${FL[c.team]||''} ${c.team}</td>
    <td><span class="pb" style="width:130px"><i style="width:${Math.min(c.p*350,100)}%"></i></span>${(c.p*100).toFixed(1)}%</td>
    <td style="color:var(--gold);font-weight:600">${odds(c.p)}</td></tr>`;
  }
  return h + '</table><p class="note">Knockout bracket approximated via Elo seeding per simulation; group-stage probabilities are exact to the model.</p>';
}
const views = {matches:vMatches,groups:vGroups,record:vRecord,power:vPower,champ:vChamp};
function show(v){
  document.getElementById('main').innerHTML = views[v]();
  document.querySelectorAll('.tabs button').forEach(b=>b.classList.toggle('on',b.dataset.v===v));
}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>show(b.dataset.v));
show('matches');
</script></body></html>"""
html = html.replace('__DATA__', DATA_JS).replace('__REC__', REC_CHIP)
open('index.html', 'w').write(html)
print('index.html:', len(html)//1024, 'KB')
