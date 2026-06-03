from __future__ import annotations
import json
import time
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import httpx
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

API_BASE = "http://localhost:8000"
REFRESH_INTERVAL = 8

st.set_page_config(
    page_title="CrisisLens",
    page_icon="🛰",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_dashboard_css(), unsafe_allow_html=True)

LABEL_DESCRIPTIONS = {
    "flood":      "Rising water levels, submerged roads, displaced families",
    "fire":       "Wildfires, building fires, evacuation orders",
    "earthquake": "Structural damage, trapped survivors, aftershocks",
    "medical":    "Injuries, casualties, urgent medical aid needed",
}

SEVERITY_GUIDE = {
    "Critical (≥0.7)": ("🔴", "Immediate response required"),
    "Elevated (0.4–0.7)": ("🟡", "Monitor closely, prepare resources"),
    "Low (<0.4)": ("🟢", "Informational, no immediate action"),
}

def fetch_events(
    label: str | None = None,
    min_severity: float = 0.0,
    limit: int = 200,
) -> list[dict]:
    params: dict = {"limit": limit, "min_severity": min_severity}
    if label:
        params["label"] = label
    try:
        resp = httpx.get(f"{API_BASE}/events", params=params, timeout=5)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception:
        return []

def render_sidebar(events: list[dict]) -> tuple[str, float]:
    with st.sidebar:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.85rem;color:#58a6ff;font-weight:600;'
            'letter-spacing:0.1em;margin-bottom:0.5rem">⬡ CRISISLENS</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:0.75rem;color:#8b949e;margin-bottom:1.5rem;'
            'line-height:1.5">'
            'Real-time AI platform that monitors social media during disasters, '
            'classifies crisis signals, and routes intelligence to responders.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.65rem;color:#484f58;letter-spacing:0.14em;'
            'margin-bottom:0.75rem">HOW IT WORKS</div>',
            unsafe_allow_html=True,
        )
        steps = [
            ("1", "Social media posts ingested in real-time"),
            ("2", "DistilBERT AI classifies crisis type + urgency"),
            ("3", "spaCy extracts locations and needs"),
            ("4", "Groq LLM explains why it flagged the event"),
            ("5", "Dashboard updates live for responders"),
        ]
        for num, desc in steps:
            st.markdown(
                f'<div style="display:flex;gap:0.6rem;margin-bottom:0.5rem;'
                f'align-items:flex-start">'
                f'<span style="font-family:\'JetBrains Mono\',monospace;'
                f'font-size:0.65rem;color:#58a6ff;background:#1f3a5f;'
                f'padding:1px 6px;border-radius:3px;flex-shrink:0">{num}</span>'
                f'<span style="font-size:0.72rem;color:#8b949e;'
                f'line-height:1.4">{desc}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.65rem;color:#484f58;letter-spacing:0.14em;'
            'margin-bottom:0.75rem">CRISIS TYPES</div>',
            unsafe_allow_html=True,
        )
        badge_colors = {
            "flood": ("#1f3a5f", "#58a6ff"),
            "fire": ("#3d1a1a", "#f85149"),
            "earthquake": ("#2d2a14", "#d29922"),
            "medical": ("#1a3d2b", "#3fb950"),
        }
        for label, desc in LABEL_DESCRIPTIONS.items():
            bg, fg = badge_colors[label]
            st.markdown(
                f'<div style="margin-bottom:0.6rem">'
                f'<span style="font-family:\'JetBrains Mono\',monospace;'
                f'font-size:0.6rem;padding:2px 7px;border-radius:3px;'
                f'background:{bg};color:{fg};font-weight:600">{label.upper()}</span>'
                f'<div style="font-size:0.68rem;color:#484f58;'
                f'margin-top:3px;line-height:1.3">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.65rem;color:#484f58;letter-spacing:0.14em;'
            'margin-bottom:0.75rem">SEVERITY GUIDE</div>',
            unsafe_allow_html=True,
        )
        for level, (icon, meaning) in SEVERITY_GUIDE.items():
            st.markdown(
                f'<div style="margin-bottom:0.5rem">'
                f'<span style="font-size:0.75rem">{icon}</span> '
                f'<span style="font-size:0.7rem;color:#c9d1d9">{level}</span>'
                f'<div style="font-size:0.65rem;color:#484f58;'
                f'margin-left:1.4rem">{meaning}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.65rem;color:#484f58;letter-spacing:0.14em;'
            'margin-bottom:0.75rem">FILTERS</div>',
            unsafe_allow_html=True,
        )
        label_options = ["all", "flood", "fire", "earthquake", "medical"]
        selected_label = st.selectbox(
            "Crisis Type",
            label_options,
            index=0,
            key="label_sel",
        )
        min_sev = st.slider(
            "Minimum Severity",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            key="sev_slider",
            help="0 = show all events · 0.7 = critical only",
        )
        st.markdown("---")
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;'
            'font-size:0.6rem;color:#30363d;text-align:center;'
            'margin-top:1rem">POWERED BY<br>'
            'DistilBERT · spaCy · Groq<br>'
            'FAISS · FastAPI · Streamlit</div>',
            unsafe_allow_html=True,
        )
    return selected_label, min_sev

def render_header(event_count: int) -> None:
    st.markdown(
        f"""
        <div class="cl-header">
            <div>
                <div class="cl-logo">⬡ CrisisLens</div>
                <div class="cl-tagline">
                    Real-Time Disaster Intelligence Platform
                </div>
            </div>
            <div style="text-align:right">
                <div class="cl-status">LIVE INGESTION ACTIVE</div>
                <div style="font-family:'JetBrains Mono',monospace;
                    font-size:0.65rem;color:#8b949e;margin-top:2px">
                    LLM · GROQ llama-3.1-8b &nbsp;·&nbsp; RAG · FAISS L2
                </div>
                <div class="cl-tagline" style="margin-top:4px">
                    {event_count} events indexed &nbsp;·&nbsp;
                    last refresh {datetime.now(timezone.utc).strftime("%H:%M:%S")} UTC
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_kpis(events: list[dict]) -> None:
    total    = len(events)
    high     = sum(1 for e in events if float(e.get("severity", 0)) >= 0.7)
    medium   = sum(1 for e in events if 0.4 <= float(e.get("severity", 0)) < 0.7)
    override = sum(1 for e in events if e.get("human_override"))
    avg_sev  = (
        sum(float(e.get("severity", 0)) for e in events) / total
    ) if total else 0.0
    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-tile kpi-total">
                <div class="kpi-label">Total Events Detected</div>
                <div class="kpi-value">{total}</div>
                <div class="kpi-sub">avg urgency score {avg_sev:.2f} / 1.00</div>
            </div>
            <div class="kpi-tile kpi-high">
                <div class="kpi-label">🔴 Critical — Act Now</div>
                <div class="kpi-value">{high}</div>
                <div class="kpi-sub">severity ≥ 0.7 · immediate response</div>
            </div>
            <div class="kpi-tile kpi-medium">
                <div class="kpi-label">🟡 Elevated — Monitor</div>
                <div class="kpi-value">{medium}</div>
                <div class="kpi-sub">severity 0.4–0.7 · prepare resources</div>
            </div>
            <div class="kpi-tile kpi-override">
                <div class="kpi-label">⚑ Needs Human Review</div>
                <div class="kpi-value">{override}</div>
                <div class="kpi-sub">AI confidence low · verify before acting</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_feed(events: list[dict], selected_label: str, min_sev: float) -> None:
    filtered = [
        e for e in events
        if float(e.get("severity", 0)) >= min_sev
        and (selected_label == "all" or selected_label in e.get("labels", []))
    ]
    filtered_sorted = sorted(
        filtered, key=lambda x: float(x.get("severity", 0)), reverse=True
    )
    st.markdown(
        f'<div class="section-header">Live Event Feed '
        f'<span style="float:right;color:#484f58">'
        f'showing {len(filtered_sorted)} events · '
        f'sorted by urgency</span></div>',
        unsafe_allow_html=True,
    )
    badge_map = {
        "flood": "badge-flood",
        "fire": "badge-fire",
        "earthquake": "badge-earthquake",
        "medical": "badge-medical",
    }
    cards_html = ""
    for event in filtered_sorted[:40]:
        sev = float(event.get("severity", 0.0))
        sev_cls = "sev-high" if sev >= 0.7 else "sev-medium" if sev >= 0.4 else "sev-low"
        override_cls = " override" if event.get("human_override") else ""
        labels_html = "".join(
            f'<span class="label-badge {badge_map.get(lbl, "")}">{lbl}</span>'
            for lbl in event.get("labels", [])
        )
        loc_str = event.get("location_raw") or ""
        loc_html = (
            f'<span class="card-location">📍 {loc_str}</span>'
            if loc_str else ""
        )
        time_str = ""
        if event.get("indexed_at"):
            try:
                dt = datetime.fromisoformat(
                    str(event["indexed_at"]).replace("Z", "")
                )
                time_str = dt.strftime("%H:%M:%S")
            except Exception:
                pass
        sev_pct = int(sev * 100)
        sev_color = (
            "#f85149" if sev >= 0.7 else
            "#d29922" if sev >= 0.4 else
            "#238636"
        )
        sev_label = (
            "CRITICAL" if sev >= 0.7 else
            "ELEVATED" if sev >= 0.4 else
            "LOW"
        )
        sev_bar = (
            f'<div class="sev-bar-wrap">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;'
            f'font-size:0.58rem;color:{sev_color};margin-right:4px">'
            f'{sev_label}</div>'
            f'<div class="sev-bar-bg">'
            f'<div class="sev-bar-fill" '
            f'style="width:{sev_pct}%;background:{sev_color}"></div>'
            f'</div>'
            f'<div class="sev-value">{sev:.2f}</div>'
            f'</div>'
        )
        reasoning_html = ""
        if event.get("reasoning"):
            reasoning_html = (
                f'<div class="card-reasoning">'
                f'<span style="color:#58a6ff;font-size:0.68rem;'
                f'font-family:\'JetBrains Mono\',monospace">WHY FLAGGED</span> · '
                f'{event["reasoning"]}'
                f'</div>'
            )
        action_html = ""
        if event.get("recommended_action"):
            action_html = (
                f'<div class="card-action">'
                f'<span style="color:#8b949e">RECOMMENDED ACTION</span> · '
                f'{event["recommended_action"]}'
                f'</div>'
            )
        override_html = (
            '<span class="override-flag">⚑ NEEDS HUMAN REVIEW</span>'
            if event.get("human_override") else ""
        )
        cards_html += (
            f'<div class="crisis-card {sev_cls}{override_cls}">'
            f'<div class="card-meta">'
            f'{labels_html}{override_html}{loc_html}'
            f'<span class="card-time">{time_str}</span>'
            f'{sev_bar}'
            f'</div>'
            f'<div class="card-text">{event.get("text", "")}</div>'
            f'{reasoning_html}'
            f'{action_html}'
            f'</div>'
        )
    if not cards_html:
        cards_html = (
            '<div style="font-family:monospace;font-size:0.75rem;'
            'color:#484f58;padding:2rem;text-align:center">'
            'NO EVENTS MATCH CURRENT FILTERS<br>'
            '<span style="font-size:0.65rem">Try lowering the severity '
            'threshold or selecting "all" crisis types</span>'
            '</div>'
        )
    st.markdown(
        f'<div class="feed-scroll">{cards_html}</div>',
        unsafe_allow_html=True,
    )

def main() -> None:
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = 0.0

    events = fetch_events()
    selected_label, min_sev = render_sidebar(events)
    render_header(len(events))
    render_kpis(events)

    left_col, right_col = st.columns([3, 2], gap="medium")

    with left_col:
        st.markdown(
            '<div class="section-header">Where Are Crises Happening? '
            '<span style="float:right;color:#484f58;font-weight:400">'
            'click markers for details</span></div>',
            unsafe_allow_html=True,
        )
        folium_map = build_map(events)
        st_folium(
            folium_map,
            width=None,
            height=420,
            returned_objects=[],
            key="crisis_map",
        )
        st.markdown(
            '<div style="font-size:0.68rem;color:#484f58;margin-top:0.3rem;'
            'font-family:\'JetBrains Mono\',monospace">'
            '🔴 critical &nbsp;·&nbsp; 🟡 elevated &nbsp;·&nbsp; 🟢 low '
            '&nbsp;·&nbsp; clusters show multiple nearby events'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-header" style="margin-top:1.5rem">'
            'Urgency Over Time '
            '<span style="float:right;color:#484f58;font-weight:400">'
            'spikes = mass casualty events</span></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            severity_timeline(events),
            use_container_width=True,
            config={"displayModeBar": False},
            key="timeline_chart",
        )

        chart_l, chart_r = st.columns(2)
        with chart_l:
            st.markdown(
                '<div style="font-size:0.65rem;color:#484f58;'
                'font-family:\'JetBrains Mono\',monospace;margin-bottom:0.3rem">'
                'WHAT KINDS OF CRISES?</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                label_distribution(events),
                use_container_width=True,
                config={"displayModeBar": False},
                key="label_chart",
            )
        with chart_r:
            st.markdown(
                '<div style="font-size:0.65rem;color:#484f58;'
                'font-family:\'JetBrains Mono\',monospace;margin-bottom:0.3rem">'
                'AI CONFIDENCE — does it need human check?</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                override_donut(events),
                use_container_width=True,
                config={"displayModeBar": False},
                key="override_chart",
            )

        st.markdown(
            '<div style="font-size:0.65rem;color:#484f58;'
            'font-family:\'JetBrains Mono\',monospace;margin-bottom:0.3rem">'
            'HOW URGENT ARE EVENTS? (0 = low · 1 = critical)</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            severity_histogram(events),
            use_container_width=True,
            config={"displayModeBar": False},
            key="hist_chart",
        )

    with right_col:
        render_feed(events, selected_label, min_sev)

    if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
        st.session_state.last_refresh = time.time()
        st.rerun()

if __name__ == "__main__":
    main()
