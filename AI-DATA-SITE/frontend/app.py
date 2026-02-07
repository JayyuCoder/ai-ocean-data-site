from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
import plotly.express as px

st.set_page_config(
    page_title="AI Ocean Data Dashboard",
    page_icon="AI",
    layout="wide"
)

st.title("Coral Reef Health Monitor")
st.markdown("Real-time AI-powered ocean health monitoring")

# API Base URL
API_URL = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.header("Settings")
    time_range = st.slider("Days to display", 1, 90, 30)
    refresh_interval = st.selectbox("Refresh interval", ["5s", "30s", "1m", "5m"])

# Main dashboard
tabs = st.tabs(["Overview", "Map View", "Analytics", "Anomalies"])

# TAB 1: Overview
with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)

    try:
        stats = requests.get(f"{API_URL}/stats").json()
        with col1:
            st.metric("Avg SST (C)", f"{stats['avg_sst']:.2f}")
        with col2:
            st.metric("Avg pH", f"{stats['avg_ph']:.2f}")
        with col3:
            st.metric("Avg Health Score", f"{stats['avg_health_score']:.1f}")
        with col4:
            st.metric("Anomalies Detected", stats["anomalies_detected"])
    except Exception:
        st.error("Unable to connect to API")

    st.divider()

    # Latest data
    try:
        latest = requests.get(f"{API_URL}/data/latest").json()
        if "error" in latest:
            st.info("No latest data available yet")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"Latest: {latest.get('date')}")
            with col2:
                if latest.get("anomaly"):
                    st.warning("ANOMALY DETECTED")
                else:
                    st.success("Normal")
    except Exception:
        pass

# TAB 2: Map View
with tabs[1]:
    try:
        # Fetch latest data
        data = requests.get(f"{API_URL}/data/timeseries?days={time_range}").json()

        if isinstance(data, list) and data:
            df = pd.DataFrame(data)

            # Create pydeck map
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=pdk.ViewState(
                        latitude=df["latitude"].mean(),
                        longitude=df["longitude"].mean(),
                        zoom=3,
                        pitch=30,
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=df,
                            get_position="[longitude, latitude]",
                            get_color="[health_score * 2.55, 255 - health_score * 2.55, 0]",
                            get_radius=50000,
                            pickable=True,
                        )
                    ],
                    tooltip={
                        "text": "SST: {sst} C\nPH: {ph}\nHealth: {health_score}%"
                    },
                )
            )
        else:
            st.warning("No spatial data available")
    except Exception as e:
        st.error(f"Map error: {e}")

# TAB 3: Analytics
with tabs[2]:
    try:
        data = requests.get(f"{API_URL}/data/timeseries?days={time_range}").json()

        if isinstance(data, list) and data:
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])

            col1, col2 = st.columns(2)

            with col1:
                # SST trend
                fig_sst = px.line(df, x="date", y="sst", title="Sea Surface Temperature Trend")
                st.plotly_chart(fig_sst, use_container_width=True)

            with col2:
                # pH trend
                fig_ph = px.line(df, x="date", y="ph", title="pH Trend")
                st.plotly_chart(fig_ph, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                # Health Score
                fig_health = px.line(df, x="date", y="health_score", title="Reef Health Score")
                st.plotly_chart(fig_health, use_container_width=True)

            with col2:
                # Anomaly Distribution
                anomaly_counts = df["anomaly"].value_counts()
                fig_anomaly = px.pie(
                    values=anomaly_counts.values,
                    names=[("Anomaly" if x else "Normal") for x in anomaly_counts.index],
                    title="Data Distribution",
                )
                st.plotly_chart(fig_anomaly, use_container_width=True)
    except Exception:
        st.error("Analytics data unavailable")

# TAB 4: Anomalies
with tabs[3]:
    try:
        anomalies = requests.get(f"{API_URL}/data/anomalies").json()

        if isinstance(anomalies, list) and anomalies:
            df_anomalies = pd.DataFrame(anomalies)
            st.warning(f"{len(anomalies)} anomalies detected")
            st.dataframe(df_anomalies, use_container_width=True)
        else:
            st.success("No anomalies detected")
    except Exception:
        st.error("Unable to fetch anomalies")

st.divider()
st.caption("AI Ocean Data Site | Real-time Monitoring | Powered by NOAA + ML")
