# 🚁 Drone Flight Data Visualizer

A simple Python app that turns raw drone telemetry logs into clean graphs and flight maps in seconds.

**👉 [Try the Live Demo](https://droneviz.streamlit.app/)**

## ⚡ What it does
- **Upload & Clean:** Upload messy raw drone data (JSON or CSV). The app cleans and combines.
- **Auto-detect:** Automatically finds columns for altitude, speed, battery, and GPS.
- **Visualize:** Generates performance graphs and a flight path map.
- **Export:** Download your cleaned dataset as a CSV.

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📂 Sample Data
The `sample_data/` folder contains a test file you can upload to try it out.  

*(Sample data adapted from the [UAV Telemetry Dataset](https://doi.org/10.5281/zenodo.15912415) by Díez Tomillo et al. under CC BY 4.0).*