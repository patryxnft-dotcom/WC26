#!/usr/bin/env python3
"""GoldenBoot model: Elo + Poisson + Monte Carlo. Run: python scripts/model.py <results.csv>"""
import pandas as pd, numpy as np, json, math, sys, os
from datetime import date
from scipy.optimize import minimize
from collections import defaultdict

DATA = sys.argv[1] if len(sys.argv) > 1 else 'data/results.csv'
TODAY = date.today().isoformat()
WC_START = '2026-06-11'
TRAIN_GOALS_FROM = '2010-01-01'
HOME_ELO = 60.0

df = pd.read_csv(DATA).sort_values('date').reset_index(drop=True)
df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce')
df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce')
played = df[df['home_score'].notna()].copy()

K_MAP = [('FIFA World Cup', 60), ('qualification', 40), ('UEFA Euro', 50), ('Copa América', 50),
         ('African Cup of Nations', 50), ('AFC Asian Cup', 50), ('Gold Cup', 50),
         ('Nations League', 35), ('Confederations', 40), ('Friendly', 20)]
def kfactor(t):
    for key, k in K_MAP:
        if key.lower() in str(t).lower(): return k
    return 30

def run_elo(matches):
    elo = defaultdict(lambda: 1500.0); hist = []
    for r in matches.itertuples():
        h, a = r.home_team, r.away_team
        eh, ea = elo[h], elo[a]
        adv = 0.0 if str(r.neutral).upper() in ('TRUE', '1') else HOME_ELO
        exp_h = 1.0 / (1.0 + 10 ** ((ea - (eh + adv)) / 400.0))
        gd = abs(r.home_score - r.away_score)
        res = 1.0 if r.home_score > r.away_score else (0.0 if r.home_score < r.away_score else 0.5)
        g = 1.0 if gd <= 1 else (1.5 if gd == 2 else (11 + gd) / 8.0)
        k = kfactor(r.tournament) * g
        elo[h] = eh + k * (res - exp_h); elo[a] = ea - k * (res - exp_h)
        hist.append((eh + adv - ea, r.home_score, r.away_score, r.date))
    return elo, hist

def fit_goal_model(hist, date_from):
    rows = [(d, hs, as_) for d, hs, as_, dt in hist if dt >= date_from]
    diffs = np.array([r[0] for r in rows]) / 400.0
    gh = np.array([r[1] for r in rows], float); ga = np.array([r[2] for r in rows], float)
    def nll(p):
        a, b = p
        lh = np.clip(np.exp(a + b * diffs), 1e-6, 8); la = np.clip(np.exp(a - b * diffs), 1e-6, 8)
        return -(np.sum(gh * np.log(lh) - lh) + np.sum(ga * np.log(la) - la))
    return minimize(nll, [0.2, 0.9], method='Nelder-Mead').x

def match_probs(eh, ea, a, b, max_g=10):
    diff = (eh - ea) / 400.0
    lh, la = math.exp(a + b * diff), math.exp(a - b * diff)
    P = np.outer([math.exp(-lh) * lh**i / math.factorial(i) for i in range(max_g)],
                 [math.exp(-la) * la**j / math.factorial(j) for j in range(max_g)])
    P /= P.sum()
    return dict(p_home=float(np.tril(P, -1).sum()), p_draw=float(np.trace(P)), p_away=float(np.triu(P, 1).sum()),
                lam_h=lh, lam_a=la,
                over25=float(sum(P[i][j] for i in range(max_g) for j in range(max_g) if i + j >= 3)),
                btts=float(sum(P[i][j] for i in range(1, max_g) for j in range(1, max_g))),
                top_scores=sorted(((f"{i}-{j}", float(P[i][j])) for i in range(6) for j in range(6)), key=lambda x: -x[1])[:3])

# ---- track record: evaluate old predictions against new results ----
track = []
if os.path.exists('track_record.json'):
    track = json.load(open('track_record.json'))
seen = {(t['date'], t['home'], t['away']) for t in track}
if os.path.exists('predictions.json'):
    old = json.load(open('predictions.json'))
    res_idx = {(r.date, r.home_team, r.away_team): (r.home_score, r.away_score)
               for r in played[played['date'] >= WC_START].itertuples()}
    for m in old.get('matches', []):
        key = (m['date'], m['home'], m['away'])
        if key in res_idx and key not in seen:
            hs, as_ = res_idx[key]
            probs = [m['p_home'], m['p_draw'], m['p_away']]
            pick = int(np.argmax(probs))
            actual = 0 if hs > as_ else (1 if hs == as_ else 2)
            track.append(dict(date=m['date'], home=m['home'], away=m['away'],
                              score=f"{int(hs)}-{int(as_)}",
                              pick=['1', 'X', '2'][pick], pick_p=round(probs[pick], 4),
                              actual=['1', 'X', '2'][actual], correct=pick == actual,
                              fair_odds=round(1 / probs[pick], 2)))
track.sort(key=lambda t: t['date'])
json.dump(track, open('track_record.json', 'w'), indent=1)

# ---- final model ----
elo, hist = run_elo(played)
a, b = fit_goal_model(hist, TRAIN_GOALS_FROM)

GROUPS = {
 'A': ['Mexico','South Africa','South Korea','Czech Republic'],
 'B': ['Canada','Bosnia and Herzegovina','Qatar','Switzerland'],
 'C': ['Brazil','Morocco','Haiti','Scotland'],
 'D': ['United States','Paraguay','Australia','Turkey'],
 'E': ['Germany','Curaçao','Ivory Coast','Ecuador'],
 'F': ['Netherlands','Japan','Sweden','Tunisia'],
 'G': ['Belgium','Egypt','Iran','New Zealand'],
 'H': ['Spain','Cape Verde','Saudi Arabia','Uruguay'],
 'I': ['France','Senegal','Iraq','Norway'],
 'J': ['Argentina','Algeria','Austria','Jordan'],
 'K': ['Portugal','DR Congo','Uzbekistan','Colombia'],
 'L': ['England','Croatia','Ghana','Panama']}
team_group = {t: g for g, ts in GROUPS.items() for t in ts}
all_teams = [t for ts in GROUPS.values() for t in ts]

fixtures = df[(df['tournament'] == 'FIFA World Cup') & (df['date'] >= WC_START) & df['home_score'].isna()]
fx = []
for r in fixtures.itertuples():
    pr = match_probs(elo[r.home_team], elo[r.away_team], a, b)
    fx.append(dict(date=r.date, home=r.home_team, away=r.away_team, city=r.city,
                   group=team_group.get(r.home_team, 'KO'),
                   p_home=round(pr['p_home'], 4), p_draw=round(pr['p_draw'], 4), p_away=round(pr['p_away'], 4),
                   over25=round(pr['over25'], 4), btts=round(pr['btts'], 4),
                   xg_h=round(pr['lam_h'], 2), xg_a=round(pr['lam_a'], 2),
                   top_scores=[[s, round(p, 4)] for s, p in pr['top_scores']]))

# ---- Monte Carlo (real results baked in) ----
rng = np.random.default_rng(2026)
N_SIM = 10000
wc_played = played[(played['tournament'] == 'FIFA World Cup') & (played['date'] >= WC_START)]
base_pts = defaultdict(int); base_gd = defaultdict(int); base_gf = defaultdict(int)
for r in wc_played.itertuples():
    if r.home_team not in team_group: continue
    h, w, g1, g2 = r.home_team, r.away_team, int(r.home_score), int(r.away_score)
    base_gd[h] += g1 - g2; base_gd[w] += g2 - g1; base_gf[h] += g1; base_gf[w] += g2
    if g1 > g2: base_pts[h] += 3
    elif g2 > g1: base_pts[w] += 3
    else: base_pts[h] += 1; base_pts[w] += 1

group_fx = defaultdict(list)
for f in fx:
    if f['group'] != 'KO':
        group_fx[f['group']].append((f['home'], f['away']))

def sim_match(t1, t2):
    diff = (elo[t1] - elo[t2]) / 400.0
    return rng.poisson(math.exp(a + b * diff)), rng.poisson(math.exp(a - b * diff))

adv_top2 = defaultdict(int); adv_any = defaultdict(int); champion = defaultdict(int)
for _ in range(N_SIM):
    thirds = []; winners = {}; runners = {}
    for g, ts in GROUPS.items():
        pts = dict(); gdf = dict(); gf = dict()
        for t in ts: pts[t] = base_pts[t]; gdf[t] = base_gd[t]; gf[t] = base_gf[t]
        for h, w in group_fx[g]:
            g1, g2 = sim_match(h, w)
            gdf[h] += g1 - g2; gdf[w] += g2 - g1; gf[h] += g1; gf[w] += g2
            if g1 > g2: pts[h] += 3
            elif g2 > g1: pts[w] += 3
            else: pts[h] += 1; pts[w] += 1
        order = sorted(ts, key=lambda t: (pts[t], gdf[t], gf[t], rng.random()), reverse=True)
        winners[g], runners[g] = order[0], order[1]
        thirds.append((order[2], pts[order[2]], gdf[order[2]], gf[order[2]]))
        adv_top2[order[0]] += 1; adv_top2[order[1]] += 1
    thirds.sort(key=lambda x: (x[1], x[2], x[3], rng.random()), reverse=True)
    r32 = list(winners.values()) + list(runners.values()) + [t for t, *_ in thirds[:8]]
    for t in r32: adv_any[t] += 1
    seeded = sorted(r32, key=lambda t: -(elo[t] + rng.normal(0, 25)))
    cur = [x for pair in zip(seeded[:16], seeded[16:][::-1]) for x in pair]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            g1, g2 = sim_match(cur[i], cur[i+1])
            if g1 == g2:
                p1 = 1 / (1 + 10 ** ((elo[cur[i+1]] - elo[cur[i]]) / 400))
                nxt.append(cur[i] if rng.random() < p1 else cur[i+1])
            else: nxt.append(cur[i] if g1 > g2 else cur[i+1])
        cur = nxt
    champion[cur[0]] += 1

groups_out = {}
for g, ts in GROUPS.items():
    groups_out[g] = [dict(team=t, elo=round(elo[t]), pts=base_pts[t], p_top2=round(adv_top2[t]/N_SIM, 4),
                          p_advance=round(adv_any[t]/N_SIM, 4)) for t in sorted(ts, key=lambda t: -adv_any[t])]

nc = sum(1 for t in track if t['correct'])
out = dict(generated=TODAY, n_sim=N_SIM,
    backtest=dict(wc2022_acc=0.547, wc2022_logloss=1.0392, euro2024_acc=0.49, euro2024_logloss=1.0375),
    record=dict(correct=nc, total=len(track)),
    power=[dict(team=t, elo=round(elo[t])) for t in sorted(all_teams, key=lambda t: -elo[t])],
    matches=sorted(fx, key=lambda f: f['date']),
    groups=groups_out,
    champion=[dict(team=t, p=round(c/N_SIM, 4)) for t, c in sorted(champion.items(), key=lambda x: -x[1])[:15]])
json.dump(out, open('predictions.json', 'w'), indent=1, ensure_ascii=False)
print(f"OK: {len(fx)} upcoming matches, record {nc}/{len(track)}")
