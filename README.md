# Air Quality Visualisation — Group Project

Interactive visualisation dashboards built for the **UCI Air Quality dataset**, exploring pollution patterns, environmental correlations, and anomalies across time. Three independently designed systems each address the same six analytical tasks from different visual perspectives.

---

## Dataset

**Source:** [UCI Air Quality Dataset](https://archive.ics.uci.edu/ml/datasets/Air+Quality)
**File:** `air+quality (1)/AirQualityUCI.csv`
**Coverage:** March 2004 – April 2005, hourly readings from an Italian city
**Size:** ~9,326 valid rows after cleaning (missing values encoded as `-200`)

| Column | Pollutant / Variable |
|--------|----------------------|
| CO(GT) | Carbon Monoxide |
| C6H6(GT) | Benzene |
| NOx(GT) | Nitrogen Oxides |
| NO2(GT) | Nitrogen Dioxide |
| T | Temperature (°C) |
| RH | Relative Humidity (%) |

---

## Six Analytical Tasks

Each system is designed to address all six tasks:

| # | Task |
|---|------|
| T1 | At what hour/day does each pollutant peak? |
| T2 | Are there long-term rising or falling trends over time? |
| T3 | What does the daily behavioural cycle of pollution look like? |
| T4 | Which pollutant dominates in the morning vs. at night? |
| T5 | How do temperature and humidity influence concentrations? |
| T6 | Where are the abnormal / anomalous readings? (>2σ above mean) |

---

## Systems

### System A — Temporal Pattern Explorer

**File:** `system A.html`
**Tech:** Vega-Lite 5.20.1 (self-contained, no server needed)

A four-view coordinated dashboard driven by a **pollutant dropdown** and an **interval brush** on the time series.

| View | Position | Description | Tasks |
|------|----------|-------------|-------|
| Time Series | Top | Daily average concentration with crimson anomaly dots | T2, T6 |
| Heatmap | Mid-left | Hour-of-day × weekday grid (orange-red scale) | T1, T3 |
| Scatter | Mid-right | Temperature vs. concentration, coloured by humidity (blue scale) + loess trend | T5 |
| Grouped Bar | Bottom | Morning (7–10h) vs. night (21–2h) normalised fold comparison | T4 |

**Interaction:** Drag a time range on the top time series → heatmap and scatter update to show only that period.

---

### System B — Click-Based Explorer

**File:** `system B.html`
**Tech:** Vega-Lite (self-contained)

An alternative design using **click-point selection** instead of an interval brush. Uses a viridis colour scheme with a focus on NO2 and a timeline line chart as the primary temporal view.

---

### System C — Air Quality Analysis Dashboard

**File:** `system_c.html`
**Tech:** Vega-Lite 4 (self-contained)

A three-panel layout with styled dropdowns for filtering by **Day** and **Pollutant Type**.

| Panel | Description | Tasks |
|-------|-------------|-------|
| T1: Hourly Levels | Bar chart of concentration by hour — click a bar to select an entire time period | T1, T3 |
| T2: Period Composition | Stacked/grouped bar showing the relative mix of pollutants in the selected period | T2, T4 |
| T3: Environmental Correlations | Scatter matrix (T, RH, AH vs. concentration) — brush to cross-filter the bar charts | T5 |

**Interaction:** Brush the scatter plots to highlight corresponding bars; click a bar to generalise the period selection.

---

## Design Comparison

| Feature | System A | System B | System C |
|---------|----------|----------|----------|
| Temporal view | Heatmap (hour × weekday) | Line chart timeline | Hourly bar chart |
| Primary interaction | Interval brush on time axis | Click point selection | Click + scatter brush |
| Colour scheme | Orange-red / Blues | Viridis | Blue accent |
| T4 comparison | Grouped bar (morning vs night) | — | Period composition |
| T5 trend | Loess curve | Plain scatter | Scatter matrix |
| Anomaly highlight | Crimson dots (T6) | — | — |

---

## How to Open

All three files are fully self-contained HTML — no installation or server required.

1. Clone or download this repository
2. Open any `.html` file directly in a modern browser (Chrome or Firefox recommended)
3. Use the dropdowns and interactive elements to explore

```bash
git clone https://github.com/pubaaaali/Air-Quality-Visualisation.git
cd Air-Quality-Visualisation
open "system A.html"   # macOS
# or double-click the file in your file explorer
```

---

## Files

```
.
├── system A.html              # System A dashboard
├── system B.html              # System B dashboard
├── system_c.html              # System C dashboard
├── gen_system_a.py            # Python script to regenerate System A
├── 6 tasks.docx               # Task specification document
└── air+quality (1)/
    └── AirQualityUCI.csv      # UCI Air Quality dataset
```

---

## Generator Script

`gen_system_a.py` reads `AirQualityUCI.csv`, cleans the data (removes `-200` sentinel values), computes daily averages, anomaly flags, and morning/night period aggregates, then writes the full Vega-Lite spec into `system A.html`.

```bash
python3 gen_system_a.py
```

Requires: `pandas`, `numpy`
