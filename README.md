# 🚁 Drone Flight Data Visualizer

A Python app that turns raw drone telemetry logs into clean graphs, flight maps, and anomaly reports in seconds.

**👉 [Try the Live Demo](https://droneviz.streamlit.app/)**

---

## ⚡ Features

- **Upload & Clean** — Upload raw drone data (JSON or CSV). The app cleans and combines multiple files automatically.
- **Auto-detect Columns** — Automatically finds columns for altitude, speed, battery, and GPS coordinates.
- **Performance Graphs** — Altitude, speed, and battery charts over time with a dark theme.
- **Flight Path Map** — 2D GPS map of the drone's route.
- **🛸 3D Flight Path** *(New)* — Interactive 3D visualization of the flight trajectory, color-coded by altitude using Plotly.
- **⚠️ Anomaly Detection** *(New)* — Automatically flags unusual data points (altitude spikes, battery drops, speed outliers) using z-score analysis.
- **Export** — Download your cleaned dataset as a CSV.

---

## 🛸 3D Flight Path

When GPS data (latitude & longitude) is available alongside altitude, the app renders a fully interactive 3D flight path. You can rotate, zoom, and pan to inspect the trajectory from any angle. The path is color-coded by altitude using the Plasma colorscale.

## ⚠️ Anomaly Detection

The app runs a z-score check across altitude, speed, and battery columns. Any data point more than **2.5 standard deviations** from the mean is flagged as an anomaly. Results include:
- A count of anomalies found
- A breakdown of which columns were checked
- An expandable table showing every flagged row

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📂 Sample Data

The `sample_data/` folder contains a test flight file so you can try the app without uploading anything. Just launch it and the demo loads automatically.

---

## 📋 Changelog

### v1.1.0 — April 2026
- ✅ Added **interactive 3D flight path** (Plotly `Scatter3d`, color-coded by altitude)
- ✅ Added **anomaly detection** (z-score based, across altitude / speed / battery)
- ✅ Added `plotly` and `numpy` dependencies

### v1.0.0 — Initial Release
- Upload & parse JSON / CSV drone logs
- Auto-detect telemetry columns
- Altitude, speed, battery charts (dark theme)
- 2D GPS flight path map
- CSV export

---

*(Sample data adapted from the [UAV Telemetry Dataset](https://doi.org/10.5281/zenodo.15912415) by Díez Tomillo et al. under CC BY 4.0)*