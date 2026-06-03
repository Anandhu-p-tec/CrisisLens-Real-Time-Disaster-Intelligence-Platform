from __future__ import annotations

import json
import folium
from folium.plugins import MarkerCluster

SEVERITY_COLORS: dict[str, str] = {
    "high": "#f85149",
    "medium": "#d29922",
    "low": "#238636",
}

LABEL_ICONS: dict[str, str] = {
    "flood": "tint",
    "fire": "fire",
    "earthquake": "warning-sign",
    "medical": "plus-sign",
}


def severity_class(severity: float) -> str:
    if severity >= 0.7:
        return "high"
    if severity >= 0.4:
        return "medium"
    return "low"


def build_map(events: list[dict]) -> folium.Map:
    m = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles="CartoDB dark_matter",
        control_scale=False,
    )
    cluster = MarkerCluster(
        options={
            "maxClusterRadius": 40,
            "disableClusteringAtZoom": 10,
        }
    ).add_to(m)
    for event in events:
        # Parse JSON strings to dicts
        if isinstance(event, str):
            try:
                event = json.loads(event)
            except (json.JSONDecodeError, TypeError):
                continue
        if not isinstance(event, dict):
            continue
        lat = event.get("lat")
        lng = event.get("lng")
        if lat is None or lng is None:
            continue
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            continue
        sev = float(event.get("severity", 0.0)) if event.get("severity") else 0.0
        sev_cls = severity_class(sev)
        color = SEVERITY_COLORS[sev_cls]
        labels: list[str] = event.get("labels", [])
        primary_label = labels[0] if labels else "unknown"
        icon_name = LABEL_ICONS.get(primary_label, "info-sign")
        popup_html = f"""
        <div style="font-family:monospace;font-size:11px;color:#c9d1d9;
                    background:#0d1117;padding:10px;border-radius:4px;
                    border:1px solid #1e2d3d;max-width:260px;line-height:1.6">
            <div style="color:{color};font-weight:600;margin-bottom:4px">
                {primary_label.upper()} &nbsp;·&nbsp; SEV {sev:.2f}
            </div>
            <div style="color:#8b949e;margin-bottom:6px">
                {event.get("location_raw") or "location unresolved"}
            </div>
            <div style="color:#e6edf3">{event.get("text","")[:140]}…</div>
            {f'<div style="color:#3fb950;margin-top:6px;font-size:10px">▶ {event.get("recommended_action","")}</div>' if event.get("recommended_action") else ""}
        </div>
        """
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=280),
            icon=folium.Icon(
                color="black",
                icon_color=color,
                icon=icon_name,
                prefix="glyphicon",
            ),
        ).add_to(cluster)
    return m
