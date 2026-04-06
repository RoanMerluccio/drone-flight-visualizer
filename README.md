# 🚁 Drone Flight Data Visualizer

A lightweight tool that converts raw drone telemetry logs into a clean dataset and visualizes flight performance in seconds.

## 🔗 Live Demo
[Try it here](https://droneviz.streamlit.app/)

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

## 🎥 Demo
*(Add your RepoClip or Loom video here)*

## 🧠 How It Works
1. Upload raw telemetry files  
2. Data is automatically combined and cleaned  
3. Key metrics are extracted  
4. Graphs and insights are generated  

## 📂 Example Input
This project works with raw UAV telemetry logs (JSON or CSV).  
Column names can vary — the app automatically detects relevant fields.

## 🛠 Tech Stack
- Python  
- Streamlit  
- pandas  
- matplotlib  

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py