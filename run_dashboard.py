import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from streamlit_folium import st_folium

from app.dashboard.styles import get_dashboard_css
from app.dashboard.map_builder import build_map
from app.dashboard.chart_builder import (
    severity_histogram,
    label_distribution,
    severity_timeline,
    override_donut,
)

import json
import time
from datetime import datetime

import httpx
import pandas as pd

API_BASE = "http://localhost:8000"
REFRESH_INTERVAL = 8

st.set_page_config(
    page_title="CrisisLens",
    page_icon="🛰",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(get_dashboard_css(), unsafe_allow_html=True)

st.title("🛰 CrisisLens — Live Crisis Intelligence Dashboard")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Events", "0", delta="—")
with col2:
    st.metric("Avg Severity", "—", delta="—")
with col3:
    st.metric("High Priority", "0", delta="—")
with col4:
    st.metric("Last Update", "—", delta="—")

st.markdown("---")

try:
    with st.spinner("Fetching latest events..."):
        response = httpx.get(f"{API_BASE}/events?limit=40", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, dict):
                events = data.get("data", data.get("events", []))
            elif isinstance(data, list):
                events = data
            else:
                events = []
            # Ensure events is list of dicts (parse JSON strings)
            parsed_events = []
            for e in (events or []):
                if isinstance(e, dict):
                    parsed_events.append(e)
                elif isinstance(e, str):
                    try:
                        parsed_events.append(json.loads(e))
                    except (json.JSONDecodeError, TypeError):
                        continue
            events = parsed_events
        else:
            events = []
except Exception as e:
    st.error(f"Connection failed: {e}")
    events = []

row1_col1, row1_col2 = st.columns([1.2, 1])

with row1_col1:
    st.subheader("📍 Geospatial Map")
    if events:
        map_obj = build_map(events)
        st_folium(map_obj, width=1400, height=600)
    else:
        st.info("No events to display yet. Waiting for crisis data...")

with row1_col2:
    st.subheader("📊 Severity Distribution")
    if events:
        st.plotly_chart(severity_histogram(events), use_container_width=True)
    else:
        st.info("Awaiting data...")
    
    st.subheader("🏷️ Event Types")
    if events:
        st.plotly_chart(label_distribution(events), use_container_width=True)
    else:
        st.info("Awaiting data...")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("📈 Timeline")
    if events:
        st.plotly_chart(severity_timeline(events), use_container_width=True)
    else:
        st.info("Awaiting data...")

with row2_col2:
    st.subheader("🎯 Override Actions")
    if events:
        st.plotly_chart(override_donut(events), use_container_width=True)
    else:
        st.info("Awaiting data...")

st.markdown("---")

st.subheader("🔔 Live Event Feed")

if events:
    col1_feed, col2_feed, col3_feed = st.columns(3)
    
    with col1_feed:
        labels = list(set([e.get("primary_label") for e in events if e.get("primary_label")]))
        selected_label = st.multiselect("Filter by Label", labels, default=labels[:1] if labels else [])
    
    with col2_feed:
        severities = sorted(list(set([round(e.get("severity", 0), 1) for e in events])), reverse=True)
        min_sev, max_sev = st.slider("Severity Range", 0.0, 1.0, (0.0, 1.0), 0.1)
    
    with col3_feed:
        if st.button("🔄 Manual Refresh", use_container_width=True):
            st.rerun()
    
    filtered = [
        e for e in events
        if (not selected_label or e.get("primary_label") in selected_label)
        and (min_sev <= e.get("severity", 0) <= max_sev)
    ]
    
    st.metric("Filtered Events", f"{len(filtered)}/{len(events)}")
    
    for idx, event in enumerate(filtered[:40], 1):
        with st.container(border=True):
            col_main, col_action = st.columns([5, 1])
            
            with col_main:
                severity_pct = int(event.get("severity", 0) * 100)
                st.markdown(f"**Event #{idx}** | 🔴 Severity: {severity_pct}% | Label: `{event.get('primary_label', 'N/A')}`")
                st.caption(f"📝 {event.get('text', 'N/A')[:150]}...")
                
                if event.get("locations"):
                    st.write(f"📍 **Locations**: {', '.join(event['locations'])}")
                
                if event.get("reasoning"):
                    st.write(f"🧠 **Reasoning**: {event['reasoning'].get('explanation', 'N/A')[:200]}...")
            
            with col_action:
                st.write("")
                if st.button("View", key=f"view_{idx}"):
                    st.write(event)

else:
    st.info("💫 No crisis events in the database yet. The simulator will populate them...")

col_refresh, col_stats = st.columns(2)
with col_refresh:
    auto_refresh = st.checkbox("Auto-refresh every 8s", value=False)
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

with col_stats:
    st.caption("🟢 Live Dashboard | Last update: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
