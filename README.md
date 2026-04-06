# 🚁 Drone Flight Data Visualizer

A lightweight tool that converts raw drone telemetry logs into a clean dataset and visualizes flight performance in seconds.

Built by **Roan Merluccio**

---

## 🔗 Live Demo
[Try it here](https://droneviz.streamlit.app/)

---

## ⚡ Features
- Upload multiple JSON or CSV drone log files
- Combine fragmented telemetry into one dataset
- Auto-detect key fields (time, altitude, speed, battery, GPS)
- Clean and normalize messy real-world data
- Generate performance graphs:
  - Altitude vs Time
  - Speed vs Time
  - Battery vs Time
- Visualize flight path using GPS coordinates
- Export cleaned data as CSV

---

## 🧠 How It Works
1. Upload raw telemetry files
2. Data is automatically combined and cleaned
3. Key metrics are extracted
4. Graphs and insights are generated

---

## 📂 Sample Data
A sample file is included in `sample_data/` so you can test the app right away.

The real-world test data used during development comes from a published UAV telemetry dataset:

> Díez Tomillo, J., Sáez Pérez, J., & Salva-Garcia, P. (2025).  
> *UAV Telemetry Dataset with Waypoint Navigation* [Data set].  
> Zenodo. https://doi.org/10.5281/zenodo.15912415

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
Data collected at the University of the West of Scotland as part of the INCODE project (EU grant 101093069).

---

## 🛠 Tech Stack
- Python
- Streamlit
- pandas
- matplotlib

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Structure

```
drone-flight-visualizer/
├── app.py                  # main app
├── requirements.txt        # dependencies
├── README.md               # this file
├── sample_data/
│   └── sample_flight.json  # test data
└── .streamlit/
    └── config.toml         # dark theme config
```

---

## 📸 Screenshot
*(Add a screenshot of the app here)*