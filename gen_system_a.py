#!/usr/bin/env python3
"""Generate System-A.html — Air Quality Temporal Pattern Explorer
   IV Group Project 2026 — covers T1-T6 with brush-linked Vega-Lite views
"""
import csv, json, statistics
from datetime import datetime
from collections import defaultdict

CSV_PATH = "/Users/pubaliguha/Desktop/Semester 2/project/Information Visualisation/air+quality (1)/AirQualityUCI.csv"
OUT_PATH = "/Users/pubaliguha/Desktop/Semester 2/project/Information Visualisation/System-A.html"

WEEKDAYS   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
POLLUTANTS = ['CO', 'C6H6', 'NOx', 'NO2']
MORNING_H  = set(range(7, 11))
NIGHT_H    = set(range(21, 24)) | {0, 1, 2}

def parse_f(s):
    if not s or not s.strip(): return None
    s = s.strip()
    if s == '-200': return None
    try:
        v = float(s.replace(',', '.'))
        return None if v == -200.0 else v
    except:
        return None

# ── 1. Parse CSV ──────────────────────────────────────────────────────────────
hourly = []
with open(CSV_PATH, encoding='utf-8-sig') as f:
    rdr = csv.reader(f, delimiter=';')
    next(rdr)
    for row in rdr:
        if len(row) < 14: continue
        ds, ts = row[0].strip(), row[1].strip()
        if not ds or not ts: continue
        try:
            dt = datetime.strptime(f"{ds} {ts}", "%d/%m/%Y %H.%M.%S")
        except:
            continue
        co   = parse_f(row[2])
        c6h6 = parse_f(row[5])
        nox  = parse_f(row[7])
        no2  = parse_f(row[9])
        t_   = parse_f(row[12])
        rh   = parse_f(row[13])
        if co is None and c6h6 is None and nox is None and no2 is None:
            continue
        hourly.append({
            'datetime': dt.strftime('%Y-%m-%dT%H:%M:%S'),
            'date':     dt.strftime('%Y-%m-%d'),
            'hour':     dt.hour,
            'weekday':  WEEKDAYS[dt.weekday()],
            'CO': co, 'C6H6': c6h6, 'NOx': nox, 'NO2': no2,
            'T': t_, 'RH': rh,
        })

print(f"Hourly records: {len(hourly)}")

# ── 2. Daily averages + anomaly flags ─────────────────────────────────────────
day_bkts = defaultdict(lambda: {p: [] for p in POLLUTANTS})
for r in hourly:
    for p in POLLUTANTS:
        if r[p] is not None:
            day_bkts[r['date']][p].append(r[p])

daily = []
for date in sorted(day_bkts):
    rec = {'date': date}
    for p in POLLUTANTS:
        v = day_bkts[date][p]
        rec[p] = round(sum(v)/len(v), 3) if v else None
    daily.append(rec)

for p in POLLUTANTS:
    vals = [r[p] for r in daily if r[p] is not None]
    if len(vals) < 2:
        for r in daily: r[p+'_anom'] = False
        continue
    m, s = statistics.mean(vals), statistics.stdev(vals)
    thr = m + 2*s
    for r in daily:
        r[p+'_anom'] = bool(r[p] is not None and r[p] > thr)

print(f"Daily records:  {len(daily)}")

# ── 3. Morning vs Night (all 4 pollutants, normalised to overall mean) ─────────
bkts2 = {(per, p): [] for per in ['Morning (7-10h)', 'Night (21-2h)']
                       for p in POLLUTANTS}
for r in hourly:
    for p in POLLUTANTS:
        if r[p] is not None:
            if r['hour'] in MORNING_H:
                bkts2[('Morning (7-10h)', p)].append(r[p])
            elif r['hour'] in NIGHT_H:
                bkts2[('Night (21-2h)', p)].append(r[p])

ovr = {}
for p in POLLUTANTS:
    vals = [r[p] for r in hourly if r[p] is not None]
    ovr[p] = statistics.mean(vals) if vals else 1

period = []
for (per, p), vals in bkts2.items():
    if not vals: continue
    avg = statistics.mean(vals)
    period.append({
        'period': per, 'pollutant': p,
        'value': round(avg, 3),
        'normalized': round(avg / ovr[p], 4),
    })
period.sort(key=lambda x: (x['period'], POLLUTANTS.index(x['pollutant'])))
print(f"Period records: {len(period)}")

# ── 4. Vega-Lite spec ─────────────────────────────────────────────────────────
spec = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": {
    "text": "Air Quality — Temporal Pattern Explorer",
    "fontSize": 17, "anchor": "start", "color": "#12173a"
  },
  "config": {
    "view": {"stroke": None},
    "background": "#ffffff",
    "axis": {"labelFont": "-apple-system, sans-serif",
             "titleFont": "-apple-system, sans-serif"},
    "legend": {"labelFont": "-apple-system, sans-serif",
               "titleFont": "-apple-system, sans-serif"},
    "concat": {"spacing": 20}
  },
  "datasets": {
    "hourly": hourly,
    "daily":  daily,
    "period": period,
  },
  "params": [
    {
      "name": "pollutant", "value": "CO",
      "bind": {
        "input": "select",
        "options": ["CO", "C6H6", "NOx", "NO2"],
        "labels":  ["CO (mg/m\u00b3)", "C\u2086H\u2086 (\u03bcg/m\u00b3)",
                    "NOx (ppb)", "NO\u2082 (\u03bcg/m\u00b3)"],
        "name": "Pollutant: "
      }
    }
  ],
  "vconcat": [

    # ── View 3: Daily time series + anomaly dots, brush ────────────────────
    {
      "title": {
        "text": "T2/T6  \u2014  Daily Average & Anomalies  \u00b7  drag timeline to filter heatmap & scatter",
        "fontSize": 12, "color": "#555", "anchor": "start"
      },
      "width": 870, "height": 190,
      "data": {"name": "daily"},
      "transform": [
        {"calculate": "datum[pollutant]",          "as": "conc"},
        {"calculate": "datum[pollutant + '_anom']", "as": "is_anom"}
      ],
      "layer": [
        {
          "mark": {"type": "line", "color": "#4682b4",
                   "strokeWidth": 1.5, "interpolate": "monotone"},
          "params": [{
            "name": "time_brush",
            "select": {"type": "interval", "encodings": ["x"]}
          }],
          "encoding": {
            "x": {
              "field": "date", "type": "temporal", "title": "Date",
              "axis": {"format": "%b %Y", "labelAngle": -30, "tickCount": 14}
            },
            "y": {
              "field": "conc", "type": "quantitative",
              "title": "Daily Avg Concentration",
              "axis": {"minExtent": 50}
            }
          }
        },
        {
          "transform": [{"filter": "datum.is_anom"}],
          "mark": {"type": "point", "filled": True, "color": "crimson",
                   "size": 72, "opacity": 0.85},
          "encoding": {
            "x": {"field": "date", "type": "temporal"},
            "y": {"field": "conc", "type": "quantitative"},
            "tooltip": [
              {"field": "date",  "type": "temporal",    "title": "Date",  "format": "%d %b %Y"},
              {"field": "conc",  "type": "quantitative", "title": "Avg Value", "format": ".2f"}
            ]
          }
        }
      ]
    },

    # ── hconcat: View 1 (Heatmap) + View 2 (Scatter) ──────────────────────
    {
      "hconcat": [

        # View 1 — Heatmap hour x weekday
        {
          "title": {
            "text": "T1/T3  \u2014  Avg Concentration by Hour \u00d7 Weekday",
            "fontSize": 12, "color": "#555", "anchor": "start"
          },
          "width": 390, "height": 240,
          "data": {"name": "hourly"},
          "transform": [
            {"filter": {"param": "time_brush"}},
            {"calculate": "datum[pollutant]", "as": "conc"},
            {"filter": "datum.conc !== null"},
            {
              "aggregate": [{"op": "mean", "field": "conc", "as": "avg"}],
              "groupby": ["hour", "weekday"]
            }
          ],
          "mark": "rect",
          "encoding": {
            "x": {
              "field": "hour", "type": "ordinal", "title": "Hour of Day",
              "axis": {"labelAngle": 0}
            },
            "y": {
              "field": "weekday", "type": "ordinal", "title": None,
              "sort": WEEKDAYS
            },
            "color": {
              "field": "avg", "type": "quantitative",
              "title": "Avg Conc",
              "scale": {"scheme": "orangered"},
              "legend": {"orient": "bottom", "gradientLength": 210, "titleOrient": "left"}
            },
            "tooltip": [
              {"field": "weekday", "title": "Day"},
              {"field": "hour",    "title": "Hour"},
              {"field": "avg",     "type": "quantitative", "title": "Avg", "format": ".2f"}
            ]
          }
        },

        # View 2 — Scatter + loess
        {
          "title": {
            "text": "T5  \u2014  Concentration vs Temperature  \u00b7  colour = Relative Humidity %",
            "fontSize": 12, "color": "#555", "anchor": "start"
          },
          "width": 450, "height": 240,
          "data": {"name": "hourly"},
          "transform": [
            {"filter": {"param": "time_brush"}},
            {"calculate": "datum[pollutant]", "as": "conc"},
            {"filter": "datum.conc !== null && datum.T !== null && datum.RH !== null"}
          ],
          "layer": [
            {
              "mark": {"type": "point", "opacity": 0.22, "size": 18},
              "encoding": {
                "x": {"field": "T",    "type": "quantitative", "title": "Temperature (\u00b0C)"},
                "y": {"field": "conc", "type": "quantitative", "title": "Concentration"},
                "color": {
                  "field": "RH", "type": "quantitative",
                  "title": "RH (%)",
                  "scale": {"scheme": "blues"},
                  "legend": {"orient": "bottom", "gradientLength": 210, "titleOrient": "left"}
                }
              }
            },
            {
              "transform": [{"loess": "conc", "on": "T", "bandwidth": 0.35}],
              "mark": {"type": "line", "color": "firebrick", "strokeWidth": 2.5},
              "encoding": {
                "x": {"field": "T",    "type": "quantitative"},
                "y": {"field": "conc", "type": "quantitative"}
              }
            }
          ]
        }
      ]
    },

    # ── View 4: Morning vs Night grouped bar ──────────────────────────────
    {
      "title": {
        "text": "T4  \u2014  Dominant Pollutant: Morning (7\u201310h) vs Night (21\u20132h)  \u00b7  normalised to overall mean",
        "fontSize": 12, "color": "#555", "anchor": "start"
      },
      "width": 870, "height": 200,
      "data": {"name": "period"},
      "mark": {"type": "bar", "cornerRadiusTopLeft": 2, "cornerRadiusTopRight": 2},
      "encoding": {
        "x": {
          "field": "period", "type": "nominal", "title": None,
          "axis": {"labelFontSize": 13, "labelAngle": 0},
          "sort": ["Morning (7-10h)", "Night (21-2h)"]
        },
        "xOffset": {
          "field": "pollutant", "type": "nominal",
          "sort": POLLUTANTS
        },
        "y": {
          "field": "normalized", "type": "quantitative",
          "title": "Fold of overall mean",
          "scale": {"zero": True},
          "axis": {"format": ".1f", "gridDash": [3, 3]}
        },
        "color": {
          "field": "pollutant", "type": "nominal",
          "sort": POLLUTANTS,
          "scale": {
            "domain": ["CO", "C6H6", "NOx", "NO2"],
            "range":  ["#e6550d", "#31a354", "#3182bd", "#756bb1"]
          },
          "legend": {"title": "Pollutant", "orient": "right"}
        },
        "tooltip": [
          {"field": "period",     "title": "Period"},
          {"field": "pollutant",  "title": "Pollutant"},
          {"field": "value",      "type": "quantitative", "title": "Avg Value",    "format": ".2f"},
          {"field": "normalized", "type": "quantitative", "title": "Fold of mean", "format": ".3f"}
        ]
      }
    }
  ]
}

# ── 5. Render HTML ─────────────────────────────────────────────────────────────
spec_json = json.dumps(spec, ensure_ascii=False, separators=(',', ':'))

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>System A \u2014 Air Quality Temporal Pattern Explorer</title>
  <script src="https://cdn.jsdelivr.net/npm/vega@5.28.0"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@5.20.1"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@6.26.0"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #f0f2f5; color: #333; padding: 24px 32px; min-height: 100vh;
    }
    header { margin-bottom: 18px; }
    header h1 { font-size: 1.55rem; color: #12173a; }
    header p  { font-size: .84rem; color: #666; margin-top: 4px; line-height: 1.5; }
    header p b { color: #444; }
    #vis {
      background: #fff; border-radius: 10px; padding: 20px 24px;
      box-shadow: 0 2px 14px rgba(0,0,0,.09); display: inline-block;
    }
    .vega-bind { font-size: .9rem; color: #333; margin-bottom: 8px; }
    .vega-bind select {
      font-size: .9rem; border: 1px solid #bbb; border-radius: 4px;
      padding: 3px 8px; background: #fff; cursor: pointer;
    }
  </style>
</head>
<body>
  <header>
    <h1>System A \u2014 Air Quality: Temporal Pattern Explorer</h1>
    <p>
      UCI Air Quality dataset (March\u00a02004\u2013April\u00a02005, Italy)\u00a0\u00b7\u00a0
      Select a pollutant, then <b>drag the timeline</b> to brush-filter the heatmap &amp; scatter plot.<br>
      <b>Red dots</b> in the timeline = anomalies (&gt;2\u03c3 above daily mean).
    </p>
  </header>
  <div id="vis"></div>
  <script>
    vegaEmbed('#vis', SPEC_PLACEHOLDER, {
      renderer: 'canvas',
      actions: { export: true, source: false, compiled: false, editor: false }
    }).catch(console.error);
  </script>
</body>
</html>"""

html = html.replace('SPEC_PLACEHOLDER', spec_json)

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = len(html.encode('utf-8')) / 1024
print(f"\u2713 Written to {OUT_PATH}")
print(f"  File size: {size_kb:.0f} KB")
print(f"  Hourly: {len(hourly)} | Daily: {len(daily)} | Period: {len(period)}")
