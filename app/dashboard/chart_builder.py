from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

DARK_BG = "#0d1117"
GRID_COL = "#1e2d3d"
TEXT_COL = "#8b949e"
LABEL_COLORS = {
    "flood": "#58a6ff",
    "fire": "#f85149",
    "earthquake": "#d29922",
    "medical": "#3fb950",
}


def _base_layout(title: str) -> dict:
    return dict(
        title=dict(
            text=title,
            font=dict(family="JetBrains Mono", size=11, color=TEXT_COL),
        ),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(family="JetBrains Mono", size=10, color=TEXT_COL),
        margin=dict(l=40, r=20, t=36, b=36),
        showlegend=False,
    )


def severity_histogram(events: list[dict]) -> go.Figure:
    if not events:
        fig = go.Figure()
        fig.update_layout(**_base_layout("SEVERITY DISTRIBUTION"))
        return fig
    severities = [e.get("severity", 0.5) for e in events if isinstance(e, dict)]
    severities = [float(s) if isinstance(s, (int, float)) else 0.5 for s in severities]
    fig = go.Figure(
        go.Histogram(
            x=severities,
            xbins=dict(start=0.0, end=1.0, size=0.1),
            marker_color="#58a6ff",
            marker_line_color=DARK_BG,
            marker_line_width=1,
            opacity=0.85,
        )
    )
    fig.update_layout(
        **_base_layout("SEVERITY DISTRIBUTION"),
        xaxis=dict(
            gridcolor=GRID_COL,
            zeroline=False,
            range=[0, 1.05],
            tickvals=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            title=dict(text="severity score", font=dict(size=9)),
        ),
        yaxis=dict(gridcolor=GRID_COL, zeroline=False),
    )
    return fig


def label_distribution(events: list[dict]) -> go.Figure:
    if not events:
        fig = go.Figure()
        fig.update_layout(**_base_layout("EVENT TYPES"))
        return fig
    from collections import Counter
    all_labels: list[str] = []
    for e in events:
        all_labels.extend(e.get("labels", []))
    counts = Counter(all_labels)
    priority_labels = ["flood", "fire", "earthquake", "medical"]
    ordered_labels = [l for l in priority_labels if l in counts] + [l for l in sorted(counts.keys()) if l not in priority_labels]
    values = [counts[l] for l in ordered_labels]
    colors = [LABEL_COLORS.get(l, "#8b949e") for l in ordered_labels]
    fig = go.Figure(
        go.Bar(
            x=ordered_labels,
            y=values,
            marker_color=colors,
            marker_line_color=DARK_BG,
            marker_line_width=1,
        )
    )
    fig.update_layout(
        **_base_layout("EVENT TYPES"),
        xaxis=dict(gridcolor=GRID_COL, zeroline=False),
        yaxis=dict(gridcolor=GRID_COL, zeroline=False),
    )
    return fig


def severity_timeline(events: list[dict]) -> go.Figure:
    if not events:
        fig = go.Figure()
        fig.update_layout(**_base_layout("SEVERITY OVER TIME"))
        return fig
    df = pd.DataFrame([{"time": e["indexed_at"], "severity": e["severity"]} for e in events])
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna().sort_values("time")
    fig = go.Figure(
        go.Scatter(
            x=df["time"],
            y=df["severity"],
            mode="lines+markers",
            line=dict(color="#58a6ff", width=1.5),
            marker=dict(size=4, color="#58a6ff"),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.06)",
        )
    )
    fig.update_layout(
        **_base_layout("SEVERITY OVER TIME"),
        xaxis=dict(
            gridcolor=GRID_COL,
            zeroline=False,
            showticklabels=False,
        ),
        yaxis=dict(gridcolor=GRID_COL, zeroline=False, range=[0, 1.05]),
    )
    return fig


def override_donut(events: list[dict]) -> go.Figure:
    overrides = sum(1 for e in events if e.get("human_override"))
    auto = len(events) - overrides
    if len(events) == 0:
        fig = go.Figure()
        fig.update_layout(**_base_layout("HUMAN OVERRIDE RATE"))
        return fig
    fig = go.Figure(
        go.Pie(
            labels=["Auto-resolved", "Needs Review"],
            values=[auto, overrides],
            hole=0.72,
            marker=dict(colors=["#238636", "#8b949e"]),
            textinfo="none",
        )
    )
    pct = round(overrides / len(events) * 100) if events else 0
    fig.add_annotation(
        text=f"{pct}%<br><span style='font-size:9px'>override</span>",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(family="JetBrains Mono", size=14, color="#e6edf3"),
    )
    fig.update_layout(**_base_layout("HUMAN OVERRIDE RATE"))
    return fig
