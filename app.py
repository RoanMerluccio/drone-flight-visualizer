import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# --- drone intro animation ---
st.markdown("""
<style>

/* fullscreen overlay */
#splash {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    animation: splash-fade 3.2s ease-in-out forwards;
    pointer-events: none;
}

@keyframes splash-fade {
    0%   { opacity: 0; }
    15%  { opacity: 1; }
    70%  { opacity: 1; }
    100% { opacity: 0; }
}

/* drone scales up then holds */
#splash svg {
    animation: drone-pop 3.2s ease-in-out forwards;
    filter: drop-shadow(0 0 24px rgba(255,255,255,0.4));
}

@keyframes drone-pop {
    0%   { transform: scale(0.3); opacity: 0; }
    20%  { transform: scale(1.05); opacity: 1; }
    30%  { transform: scale(1);    opacity: 1; }
    70%  { transform: scale(1);    opacity: 1; }
    100% { transform: scale(1);    opacity: 0; }
}

/* spinning rotors */
@keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
.rotor {
    animation: spin 0.3s linear infinite;
    transform-origin: center;
    transform-box: fill-box;
}

/* label under drone */
#splash-label {
    margin-top: 24px;
    color: white;
    font-size: 22px;
    font-family: sans-serif;
    letter-spacing: 4px;
    text-transform: uppercase;
    opacity: 0.9;
}
#splash-by {
    margin-top: 10px;
    color: rgba(255,255,255,0.6);
    font-size: 13px;
    font-family: sans-serif;
    letter-spacing: 2px;
}

</style>

<div id="splash">
  <svg width="200" height="200" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
    <!-- arms -->
    <line x1="80" y1="80" x2="30" y2="30" stroke="white" stroke-width="6" stroke-linecap="round"/>
    <line x1="80" y1="80" x2="130" y2="30" stroke="white" stroke-width="6" stroke-linecap="round"/>
    <line x1="80" y1="80" x2="30" y2="130" stroke="white" stroke-width="6" stroke-linecap="round"/>
    <line x1="80" y1="80" x2="130" y2="130" stroke="white" stroke-width="6" stroke-linecap="round"/>
    <!-- rotors -->
    <ellipse class="rotor" cx="30"  cy="30"  rx="22" ry="6" fill="white" opacity="0.9"/>
    <ellipse class="rotor" cx="130" cy="30"  rx="22" ry="6" fill="white" opacity="0.9"/>
    <ellipse class="rotor" cx="30"  cy="130" rx="22" ry="6" fill="white" opacity="0.9"/>
    <ellipse class="rotor" cx="130" cy="130" rx="22" ry="6" fill="white" opacity="0.9"/>
    <!-- body -->
    <rect x="62" y="62" width="36" height="36" rx="8" fill="white"/>
    <circle cx="80" cy="80" r="8" fill="#111"/>
  </svg>
  <div id="splash-label">Drone Flight Visualizer</div>
  <div id="splash-by">By: Roan Merluccio</div>
</div>
""", unsafe_allow_html=True)

st.title("Drone Flight Data Visualizer")
st.subheader("By: Roan Merluccio")

# --- minimal custom CSS (theme colours set in .streamlit/config.toml) ---
st.markdown(
    "<style>"
    "[data-testid='metric-container']{border:1px solid #30363d;border-radius:12px;padding:16px;}"
    "[data-testid='stDownloadButton'] button{background:#238636;color:white;border:none;border-radius:8px;padding:8px 20px;font-weight:600;}"
    "h2,h3{font-weight:600;}"
    "</style>",
    unsafe_allow_html=True
)


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
    df = pd.concat(frames, ignore_index=True)
    st.success(f"{len(frames)} file(s) loaded — {len(df)} rows total")
else:
    # no files uploaded — show sample data as demo
    st.info("👆 Upload your own files above, or explore the live demo below using sample data.")
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_flight.json")
    try:
        with open(sample_path) as f:
            df = pd.json_normalize(json.load(f))
        st.success("Showing sample flight data.")
    except Exception as e:
        st.warning(f"Upload a file to get started. ({e})")
        st.stop()


# --- auto-detect columns by keyword ---
def find(df, *keywords):
    for kw in keywords:
        for col in df.columns:
            if kw in col.lower():
                return col
    return None

# --- column picker (auto-filled, user can override) ---
st.subheader("Column Mapping")
NA   = "(none)"
opts = [NA] + list(df.columns)

def pick(label, guess):
    idx = opts.index(guess) if guess in opts else 0
    return st.selectbox(label, opts, index=idx)

a, b = st.columns(2)
with a:
    time_col = pick("Time",      find(df, "time", "date", "timestamp"))
    alt_col  = pick("Altitude",  find(df, "alt",  "height", "elevation"))
    lat_col  = pick("Latitude",  find(df, "lat"))
with b:
    bat_col  = pick("Battery",   find(df, "bat",  "power", "charge"))
    spd_col  = pick("Speed",     find(df, "speed", "vel"))
    lon_col  = pick("Longitude", find(df, "lon", "lng"))

# treat "(none)" as not selected
time_col = None if time_col == NA else time_col
alt_col  = None if alt_col  == NA else alt_col
bat_col  = None if bat_col  == NA else bat_col
spd_col  = None if spd_col  == NA else spd_col
lat_col  = None if lat_col  == NA else lat_col
lon_col  = None if lon_col  == NA else lon_col

if not alt_col:
    st.warning("Select an Altitude column to continue.")
    st.stop()

# --- build clean dataframe ---
clean = pd.DataFrame()
if time_col: clean["time"]    = df[time_col]
clean["altitude"]             = pd.to_numeric(df[alt_col], errors="coerce")
if bat_col:  clean["battery"] = pd.to_numeric(df[bat_col], errors="coerce")
clean["speed"] = pd.to_numeric(df[spd_col], errors="coerce") if spd_col else clean["altitude"].diff().fillna(0)

if time_col: clean = clean.sort_values("time").reset_index(drop=True)
clean = clean.dropna(subset=["altitude"])

# --- stats ---
st.subheader("Data Preview")
st.dataframe(clean.head(20))

st.subheader("Stats")
c1, c2, c3 = st.columns(3)
c1.metric("Max Altitude", f"{clean['altitude'].max():.2f}")
c2.metric("Avg Speed",    f"{clean['speed'].mean():.2f}")
if "battery" in clean.columns:
    c3.metric("Battery Drop", f"{clean['battery'].iloc[0] - clean['battery'].iloc[-1]:.2f}")

# --- graphs ---
x       = clean["time"] if "time" in clean.columns else clean.index
x_label = "time"        if "time" in clean.columns else "index"

# use dark style for all charts
plt.style.use("dark_background")

for title, col in [("Altitude", "altitude"), ("Speed", "speed"), ("Battery", "battery")]:
    if col not in clean.columns:
        continue
    st.subheader(f"{title} vs Time")
    fig, ax = plt.subplots(facecolor="#161b22")
    ax.set_facecolor("#0d1117")
    ax.plot(x, clean[col], color="#58a6ff", linewidth=1.5)
    ax.set_xlabel(x_label, color="#8b949e")
    ax.set_ylabel(col, color="#8b949e")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values(): spine.set_edgecolor("#30363d")
    st.pyplot(fig)

# --- flight path map ---
if lat_col and lon_col:
    st.subheader("Flight Path Map")
    map_df = pd.DataFrame({
        "lat": pd.to_numeric(df[lat_col], errors="coerce"),
        "lon": pd.to_numeric(df[lon_col], errors="coerce")
    }).dropna()
    st.map(map_df)

# --- export ---
st.subheader("Export")
csv = clean.to_csv(index=False)
st.download_button("Download cleaned data as CSV", csv, "flight_data.csv", "text/csv")
