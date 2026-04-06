import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# ── Page header ───────────────────────────────────────────────────────────────
st.title("Drone Flight Data Visualizer")
st.subheader("By: Roan Merluccio")



# ── File upload ───────────────────────────────────────────────────────────────
files = st.file_uploader(
    "Upload drone log files (.json or .csv)",
    type=["json", "csv"],
    accept_multiple_files=True
)

# ── Load files (or fall back to sample data) ──────────────────────────────────
def load_file(f):
    if f.name.endswith(".csv"):
        return pd.read_csv(f)
    try:
        return pd.read_json(f)
    except Exception:
        pass
    f.seek(0)
    raw = json.load(f)
    if isinstance(raw, dict):
        raw = next((v for v in raw.values() if isinstance(v, list)), [raw])
    return pd.json_normalize(raw)

if files:
    # load uploaded files
    frames = []
    for f in files:
        try:
            frames.append(load_file(f))
        except Exception as e:
            st.warning(f"Skipped {f.name}: {e}")
    if not frames:
        st.error("No valid files could be loaded.")
        st.stop()
    data = pd.concat(frames, ignore_index=True)
    st.success(f"{len(frames)} file(s) loaded — {len(data)} rows total")
else:
    # no files uploaded — show sample data as demo
    st.info("👆 Upload your own files above, or explore the live demo below using sample data.")
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_flight.json")
    try:
        with open(sample_path) as f:
            data = pd.json_normalize(json.load(f))
        st.success("Showing sample flight data.")
    except Exception as e:
        st.warning(f"Upload a file to get started. ({e})")
        st.stop()


# --- auto-detect columns by keyword ---
def find(data, *keywords):
    for kw in keywords:
        for col in data.columns:
            if kw in col.lower():
                return col
    return None

# --- column picker (auto-filled, user can override) ---
st.subheader("Column Mapping")
NONE_OPTION = "(none)"
column_options = [NONE_OPTION] + list(data.columns)

def pick(label, guess):
    idx = column_options.index(guess) if guess in column_options else 0
    return st.selectbox(label, column_options, index=idx)

col_left, col_right = st.columns(2)
with col_left:
    time_col = pick("Time",      find(data, "time", "date", "timestamp"))
    alt_col  = pick("Altitude",  find(data, "alt",  "height", "elevation"))
    lat_col  = pick("Latitude",  find(data, "lat"))
with col_right:
    bat_col  = pick("Battery",   find(data, "bat",  "power", "charge"))
    spd_col  = pick("Speed",     find(data, "speed", "vel"))
    lon_col  = pick("Longitude", find(data, "lon", "lng"))

# treat "(none)" as not selected
time_col = None if time_col == NONE_OPTION else time_col
alt_col  = None if alt_col  == NONE_OPTION else alt_col
bat_col  = None if bat_col  == NONE_OPTION else bat_col
spd_col  = None if spd_col  == NONE_OPTION else spd_col
lat_col  = None if lat_col  == NONE_OPTION else lat_col
lon_col  = None if lon_col  == NONE_OPTION else lon_col

if not alt_col:
    st.warning("Select an Altitude column to continue.")
    st.stop()

# --- build clean dataframe ---
clean_data = pd.DataFrame()
if time_col: clean_data["time"]    = data[time_col]
clean_data["altitude"]             = pd.to_numeric(data[alt_col], errors="coerce")
if bat_col:  clean_data["battery"] = pd.to_numeric(data[bat_col], errors="coerce")
clean_data["speed"] = pd.to_numeric(data[spd_col], errors="coerce") if spd_col else clean_data["altitude"].diff().fillna(0)

if time_col: clean_data = clean_data.sort_values("time").reset_index(drop=True)
clean_data = clean_data.dropna(subset=["altitude"])

# --- stats ---
st.subheader("Data Preview")
st.dataframe(clean_data.head(20))

st.subheader("Stats")
stat1, stat2, stat3 = st.columns(3)
stat1.metric("Max Altitude", f"{clean_data['altitude'].max():.2f}")
stat2.metric("Avg Speed",    f"{clean_data['speed'].mean():.2f}")
if "battery" in clean_data.columns:
    stat3.metric("Battery Drop", f"{clean_data['battery'].iloc[0] - clean_data['battery'].iloc[-1]:.2f}")

# --- graphs ---
x       = clean_data["time"] if "time" in clean_data.columns else clean_data.index
x_label = "time"        if "time" in clean_data.columns else "index"

# use dark style for all charts
plt.style.use("dark_background")

for title, col in [("Altitude", "altitude"), ("Speed", "speed"), ("Battery", "battery")]:
    if col not in clean_data.columns:
        continue
    st.subheader(f"{title} vs Time")
    fig, ax = plt.subplots(facecolor="#161b22")
    ax.set_facecolor("#0d1117")
    ax.plot(x, clean_data[col], color="#58a6ff", linewidth=1.5)
    ax.set_xlabel(x_label, color="#8b949e")
    ax.set_ylabel(col, color="#8b949e")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values(): spine.set_edgecolor("#30363d")
    st.pyplot(fig)

# --- flight path map ---
if lat_col and lon_col:
    st.subheader("Flight Path Map")
    map_data = pd.DataFrame({
        "lat": pd.to_numeric(data[lat_col], errors="coerce"),
        "lon": pd.to_numeric(data[lon_col], errors="coerce")
    }).dropna()
    st.map(map_data)

# --- export ---
st.subheader("Export")
csv = clean_data.to_csv(index=False)
st.download_button("Download cleaned data as CSV", csv, "flight_data.csv", "text/csv")
