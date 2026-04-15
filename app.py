"""
Drone Flight Data Visualizer — v2.0
Modernized UI, richer analytics, and a smoother pipeline.
By: Roan Merluccio
"""

import json
import os
from io import StringIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drone Flight Data Visualizer",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (glassy, modern, dark) ─────────────────────────────────────────
st.markdown(
    """
    <style>
    /* App background — subtle gradient */
    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #1b2a4e 0%, transparent 60%),
                    radial-gradient(900px 500px at 110% 10%, #3a1b4e 0%, transparent 55%),
                    linear-gradient(180deg, #0b0f1a 0%, #0b0f1a 100%);
        color: #e6edf3;
    }

    /* Hero header */
    .hero {
        padding: 28px 32px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(88,166,255,0.15), rgba(188,116,255,0.12));
        border: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(10px);
        margin-bottom: 18px;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #58a6ff, #bc74ff, #ff7ab6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .hero p { margin: 6px 0 0 0; color: #9aa4b2; font-size: 0.95rem; }
    .hero .badge {
        display: inline-block; padding: 2px 10px; border-radius: 999px;
        background: rgba(88,166,255,0.15); color: #8ab4ff;
        font-size: 0.72rem; font-weight: 600; margin-left: 8px;
        border: 1px solid rgba(88,166,255,0.25);
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 14px 16px;
        border-radius: 14px;
        backdrop-filter: blur(6px);
    }
    div[data-testid="stMetricValue"] { color: #e6edf3; }
    div[data-testid="stMetricLabel"] { color: #9aa4b2; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.03);
        border-radius: 10px 10px 0 0;
        padding: 8px 18px;
        border: 1px solid rgba(255,255,255,0.06);
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(88,166,255,0.2), rgba(188,116,255,0.18));
        color: #fff !important;
    }

    /* Buttons */
    .stButton>button, .stDownloadButton>button {
        border-radius: 10px;
        border: 1px solid rgba(88,166,255,0.35);
        background: linear-gradient(135deg, rgba(88,166,255,0.18), rgba(188,116,255,0.16));
        color: #e6edf3;
        font-weight: 600;
        transition: transform 0.08s ease, box-shadow 0.2s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(88,166,255,0.25);
    }

    /* Dataframes */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1220 0%, #0b0f1a 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Shared Plotly theme ───────────────────────────────────────────────────────
PLOT_BG = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,0.08)"
FONT = "#c9d1d9"
ACCENT = "#58a6ff"
ACCENT2 = "#bc74ff"


def style_fig(fig, height=380):
    fig.update_layout(
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT, family="Inter, system-ui, sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        hoverlabel=dict(bgcolor="#161b22", bordercolor="#30363d"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID)
    return fig


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _read_bytes(name: str, raw: bytes) -> pd.DataFrame:
    if name.endswith(".csv"):
        return pd.read_csv(StringIO(raw.decode("utf-8", errors="ignore")))
    try:
        return pd.read_json(StringIO(raw.decode("utf-8", errors="ignore")))
    except Exception:
        pass
    parsed = json.loads(raw.decode("utf-8", errors="ignore"))
    if isinstance(parsed, dict):
        parsed = next((v for v in parsed.values() if isinstance(v, list)), [parsed])
    return pd.json_normalize(parsed)


def load_uploaded(files):
    frames = []
    for f in files:
        try:
            frames.append(_read_bytes(f.name, f.getvalue()))
        except Exception as e:
            st.warning(f"Skipped {f.name}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else None


@st.cache_data(show_spinner=False)
def load_sample():
    path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_flight.json")
    with open(path) as f:
        return pd.json_normalize(json.load(f))


# ── Utilities ─────────────────────────────────────────────────────────────────
def auto_find(df, *keywords):
    for kw in keywords:
        for col in df.columns:
            if kw in col.lower():
                return col
    return None


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def path_distance_km(lats, lons):
    if len(lats) < 2:
        return 0.0
    lats, lons = np.asarray(lats), np.asarray(lons)
    return float(np.nansum(haversine_km(lats[:-1], lons[:-1], lats[1:], lons[1:])))


def fmt_duration(seconds):
    if seconds is None or np.isnan(seconds):
        return "—"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>🛸 Drone Flight Data Visualizer <span class="badge">v2.0</span></h1>
        <p>Modern telemetry analysis — upload logs, explore interactive charts,
        inspect 3D flight paths, and surface anomalies in seconds.
        <i>By Roan Merluccio</i></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar: Upload + settings ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Data")
    files = st.file_uploader(
        "Drone log files",
        type=["json", "csv"],
        accept_multiple_files=True,
        help="Upload one or more .json / .csv files — they'll be combined.",
    )
    use_sample = st.toggle("Use sample data", value=not bool(files))

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    anomaly_threshold = st.slider(
        "Anomaly z-score threshold", min_value=1.5, max_value=5.0, value=2.5, step=0.1
    )
    smoothing = st.slider(
        "Chart smoothing (rolling window)", min_value=1, max_value=50, value=1
    )
    show_markers = st.checkbox("Show markers on charts", value=False)

# ── Load data ─────────────────────────────────────────────────────────────────
data = None
if files:
    data = load_uploaded(files)
    if data is not None:
        st.toast(f"Loaded {len(files)} file(s), {len(data):,} rows", icon="✅")
elif use_sample:
    try:
        data = load_sample()
        st.toast("Showing sample flight data", icon="🛸")
    except Exception as e:
        st.error(f"Could not load sample data: {e}")
        st.stop()

if data is None or data.empty:
    st.info("👈 Upload files in the sidebar or enable sample data to get started.")
    st.stop()

# ── Column mapping ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🧭 Column mapping")
    NONE = "(none)"
    opts = [NONE] + list(data.columns)

    def pick(label, guess):
        idx = opts.index(guess) if guess in opts else 0
        return st.selectbox(label, opts, index=idx)

    time_col = pick("Time", auto_find(data, "time", "date", "timestamp"))
    alt_col = pick("Altitude", auto_find(data, "alt", "height", "elevation"))
    spd_col = pick("Speed", auto_find(data, "speed", "vel"))
    bat_col = pick("Battery", auto_find(data, "bat", "power", "charge"))
    lat_col = pick("Latitude", auto_find(data, "lat"))
    lon_col = pick("Longitude", auto_find(data, "lon", "lng"))

time_col = None if time_col == NONE else time_col
alt_col = None if alt_col == NONE else alt_col
spd_col = None if spd_col == NONE else spd_col
bat_col = None if bat_col == NONE else bat_col
lat_col = None if lat_col == NONE else lat_col
lon_col = None if lon_col == NONE else lon_col

if not alt_col:
    st.warning("Select an **Altitude** column in the sidebar to continue.")
    st.stop()

# ── Build clean frame ─────────────────────────────────────────────────────────
clean = pd.DataFrame()
if time_col:
    clean["time"] = pd.to_datetime(data[time_col], errors="coerce")
    if clean["time"].isna().all():
        clean["time"] = data[time_col]  # fall back to raw
clean["altitude"] = pd.to_numeric(data[alt_col], errors="coerce")
if bat_col:
    clean["battery"] = pd.to_numeric(data[bat_col], errors="coerce")
if spd_col:
    clean["speed"] = pd.to_numeric(data[spd_col], errors="coerce")
else:
    clean["speed"] = clean["altitude"].diff().abs().fillna(0)
if lat_col:
    clean["lat"] = pd.to_numeric(data[lat_col], errors="coerce")
if lon_col:
    clean["lon"] = pd.to_numeric(data[lon_col], errors="coerce")

if "time" in clean.columns:
    clean = clean.sort_values("time").reset_index(drop=True)
clean = clean.dropna(subset=["altitude"]).reset_index(drop=True)

# ── Derived metrics ───────────────────────────────────────────────────────────
duration_s = None
if "time" in clean.columns and pd.api.types.is_datetime64_any_dtype(clean["time"]):
    duration_s = (clean["time"].iloc[-1] - clean["time"].iloc[0]).total_seconds()

distance_km = 0.0
if {"lat", "lon"}.issubset(clean.columns):
    dist_df = clean[["lat", "lon"]].dropna()
    distance_km = path_distance_km(dist_df["lat"].values, dist_df["lon"].values)

# Anomalies
anom_cols = [c for c in ["altitude", "speed", "battery"] if c in clean.columns]
anom_mask = pd.Series(False, index=clean.index)
for col in anom_cols:
    std = clean[col].std()
    if std and not np.isnan(std):
        z = (clean[col] - clean[col].mean()) / std
        anom_mask |= z.abs() > anomaly_threshold
anomalies = clean[anom_mask]

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Max Altitude", f"{clean['altitude'].max():.1f}")
k2.metric("Avg Speed", f"{clean['speed'].mean():.2f}")
k3.metric("Distance", f"{distance_km:.2f} km" if distance_km else "—")
k4.metric("Duration", fmt_duration(duration_s))
k5.metric("Anomalies", f"{len(anomalies)}", delta=None)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_charts, tab_map, tab_anom, tab_data = st.tabs(
    ["📊 Overview", "📈 Charts", "🗺️ Map & 3D", "⚠️ Anomalies", "🗃️ Data & Export"]
)


def smooth(series):
    if smoothing > 1:
        return series.rolling(smoothing, min_periods=1).mean()
    return series


x = clean["time"] if "time" in clean.columns else clean.index
x_title = "Time" if "time" in clean.columns else "Index"

# ── Overview ──────────────────────────────────────────────────────────────────
with tab_overview:
    c1, c2 = st.columns((2, 1))
    with c1:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x, y=smooth(clean["altitude"]),
                name="Altitude", line=dict(color=ACCENT, width=2),
                fill="tozeroy", fillcolor="rgba(88,166,255,0.12)",
                mode="lines+markers" if show_markers else "lines",
            )
        )
        if "battery" in clean.columns:
            fig.add_trace(
                go.Scatter(
                    x=x, y=smooth(clean["battery"]),
                    name="Battery", yaxis="y2",
                    line=dict(color=ACCENT2, width=2, dash="dot"),
                )
            )
        fig.update_layout(
            title="Altitude & Battery",
            xaxis_title=x_title,
            yaxis=dict(title="Altitude"),
            yaxis2=dict(title="Battery", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.12, x=0),
        )
        st.plotly_chart(style_fig(fig, height=420), use_container_width=True)

    with c2:
        st.markdown("#### Speed distribution")
        fig = px.histogram(clean, x="speed", nbins=30, color_discrete_sequence=[ACCENT2])
        fig.update_traces(opacity=0.85)
        st.plotly_chart(style_fig(fig, height=420), use_container_width=True)

# ── Charts ────────────────────────────────────────────────────────────────────
with tab_charts:
    for title, col, color in [
        ("Altitude", "altitude", ACCENT),
        ("Speed", "speed", "#3fb950"),
        ("Battery", "battery", ACCENT2),
    ]:
        if col not in clean.columns:
            continue
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x, y=smooth(clean[col]),
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
                mode="lines+markers" if show_markers else "lines",
                name=title,
            )
        )
        # mark anomalies on this series
        if col in anom_cols and len(anomalies):
            fig.add_trace(
                go.Scatter(
                    x=anomalies["time"] if "time" in anomalies.columns else anomalies.index,
                    y=anomalies[col],
                    mode="markers",
                    marker=dict(color="#ff6b6b", size=9, symbol="x", line=dict(width=1)),
                    name="Anomaly",
                )
            )
        fig.update_layout(title=f"{title} vs {x_title}", xaxis_title=x_title, yaxis_title=title)
        st.plotly_chart(style_fig(fig, height=320), use_container_width=True)

# ── Map & 3D ──────────────────────────────────────────────────────────────────
with tab_map:
    if not ({"lat", "lon"}.issubset(clean.columns)):
        st.info("Map features require **Latitude** and **Longitude** columns.")
    else:
        gps = clean.dropna(subset=["lat", "lon"]).reset_index(drop=True)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown("#### 2D flight path")
            fig = px.scatter_mapbox(
                gps, lat="lat", lon="lon",
                color="altitude", color_continuous_scale="Plasma",
                zoom=14, height=460,
            )
            fig.update_layout(
                mapbox_style="carto-darkmatter",
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor=PLOT_BG, font=dict(color=FONT),
            )
            st.plotly_chart(fig, use_container_width=True)

        with m2:
            st.markdown("#### 3D flight path")
            if len(gps) < 2:
                st.info("Not enough points for a 3D path.")
            else:
                fig3d = go.Figure(
                    go.Scatter3d(
                        x=gps["lon"], y=gps["lat"], z=gps["altitude"],
                        mode="lines+markers",
                        line=dict(color=gps["altitude"], colorscale="Plasma", width=5),
                        marker=dict(size=2, color=gps["altitude"], colorscale="Plasma"),
                    )
                )
                fig3d.update_layout(
                    scene=dict(
                        xaxis_title="Longitude", yaxis_title="Latitude", zaxis_title="Altitude",
                        bgcolor=PLOT_BG,
                        xaxis=dict(backgroundcolor=PLOT_BG, gridcolor=GRID, color=FONT),
                        yaxis=dict(backgroundcolor=PLOT_BG, gridcolor=GRID, color=FONT),
                        zaxis=dict(backgroundcolor=PLOT_BG, gridcolor=GRID, color=FONT),
                    ),
                    paper_bgcolor=PLOT_BG, font=dict(color=FONT),
                    margin=dict(l=0, r=0, t=10, b=0), height=460,
                )
                st.plotly_chart(fig3d, use_container_width=True)

        # Animated flight replay
        with st.expander("🎬 Animated flight replay"):
            step = max(1, len(gps) // 120)  # cap frames for perf
            sub = gps.iloc[::step].reset_index(drop=True)
            sub["frame"] = sub.index
            fig = px.scatter_mapbox(
                sub, lat="lat", lon="lon",
                color="altitude", color_continuous_scale="Plasma",
                animation_frame="frame", zoom=14, height=500,
            )
            fig.update_layout(
                mapbox_style="carto-darkmatter",
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor=PLOT_BG, font=dict(color=FONT),
            )
            st.plotly_chart(fig, use_container_width=True)

# ── Anomalies ─────────────────────────────────────────────────────────────────
with tab_anom:
    a1, a2, a3 = st.columns(3)
    a1.metric("Anomalies Found", len(anomalies))
    a2.metric("Columns Checked", len(anom_cols))
    a3.metric("Threshold (z)", f"{anomaly_threshold:.1f}")

    if len(anomalies) == 0:
        st.success("No anomalies detected — flight data looks clean! ✨")
    else:
        st.warning(f"{len(anomalies)} data point(s) flagged (z > {anomaly_threshold}).")
        st.dataframe(anomalies, use_container_width=True, height=360)

# ── Data & Export ─────────────────────────────────────────────────────────────
with tab_data:
    st.markdown("#### Cleaned dataset")
    st.dataframe(clean, use_container_width=True, height=360)

    c1, c2 = st.columns(2)
    c1.download_button(
        "⬇️ Download CSV",
        clean.to_csv(index=False),
        "flight_data.csv",
        "text/csv",
        use_container_width=True,
    )
    c2.download_button(
        "⬇️ Download JSON",
        clean.to_json(orient="records", date_format="iso"),
        "flight_data.json",
        "application/json",
        use_container_width=True,
    )

    with st.expander("Summary statistics"):
        st.dataframe(clean.describe(include="all"), use_container_width=True)
