def get_dashboard_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & base ─────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0e17 !important;
    color: #c9d1d9 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
.stApp { background-color: #0a0e17 !important; }

/* ── Top header bar ───────────────────────────────────── */
.cl-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e2d3d;
    padding-bottom: 0.75rem;
    margin-bottom: 1.5rem;
}
.cl-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #58a6ff;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.cl-tagline {
    font-size: 0.7rem;
    color: #484f58;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
}
.cl-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #3fb950;
    letter-spacing: 0.06em;
}
.cl-status::before {
    content: "● ";
    animation: blink 1.4s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── KPI metric tiles ─────────────────────────────────── */
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.kpi-tile {
    flex: 1;
    background: #0d1117;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.kpi-tile::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-tile.kpi-total::before  { background: #58a6ff; }
.kpi-tile.kpi-high::before   { background: #f85149; }
.kpi-tile.kpi-medium::before { background: #d29922; }
.kpi-tile.kpi-override::before { background: #8b949e; }

.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #484f58;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #e6edf3;
    line-height: 1;
}
.kpi-sub {
    font-size: 0.68rem;
    color: #484f58;
    margin-top: 0.3rem;
}

/* ── Section headers ──────────────────────────────────── */
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #484f58;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2d3d;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

/* ── Crisis event card ────────────────────────────────── */
.crisis-card {
    background: #0d1117;
    border: 1px solid #1e2d3d;
    border-left: 3px solid #58a6ff;
    border-radius: 4px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
    transition: border-color 0.2s;
}
.crisis-card.sev-high   { border-left-color: #f85149; }
.crisis-card.sev-medium { border-left-color: #d29922; }
.crisis-card.sev-low    { border-left-color: #238636; }
.crisis-card.override   { border-left-color: #8b949e; }

.card-meta {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
}
.label-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    padding: 2px 7px;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
.badge-flood      { background: #1f3a5f; color: #58a6ff; }
.badge-fire       { background: #3d1a1a; color: #f85149; }
.badge-earthquake { background: #2d2a14; color: #d29922; }
.badge-medical    { background: #1a3d2b; color: #3fb950; }

.sev-bar-wrap {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
}
.sev-bar-bg {
    width: 60px;
    height: 4px;
    background: #1e2d3d;
    border-radius: 2px;
    overflow: hidden;
}
.sev-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: #58a6ff;
}
.sev-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #8b949e;
    width: 32px;
}

.card-text {
    font-size: 0.82rem;
    color: #c9d1d9;
    line-height: 1.5;
    margin-bottom: 0.5rem;
}
.card-reasoning {
    font-size: 0.75rem;
    color: #8b949e;
    line-height: 1.45;
    border-top: 1px solid #1e2d3d;
    padding-top: 0.5rem;
    margin-top: 0.5rem;
}
.card-action {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #3fb950;
    margin-top: 0.35rem;
}
.override-flag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #8b949e;
    background: #161b22;
    border: 1px solid #30363d;
    padding: 1px 6px;
    border-radius: 3px;
}
.card-location {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    color: #484f58;
}
.card-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #30363d;
    margin-left: auto;
}

/* ── Map panel ────────────────────────────────────────── */
.map-wrap {
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    overflow: hidden;
}

/* ── Scrollable feed ──────────────────────────────────── */
.feed-scroll {
    max-height: 68vh;
    overflow-y: auto;
    padding-right: 4px;
}
.feed-scroll::-webkit-scrollbar { width: 4px; }
.feed-scroll::-webkit-scrollbar-track { background: transparent; }
.feed-scroll::-webkit-scrollbar-thumb { background: #1e2d3d; border-radius: 2px; }

/* ── Charts ───────────────────────────────────────────── */
.chart-wrap {
    background: #0d1117;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    padding: 1rem;
}

/* ── Streamlit element overrides ──────────────────────── */
div[data-testid="stMetric"] { display: none; }
.stSelectbox > div > div {
    background: #0d1117 !important;
    border-color: #1e2d3d !important;
    color: #c9d1d9 !important;
}
.stSlider > div > div { background: #1e2d3d !important; }
button[kind="primary"] {
    background: #1f3a5f !important;
    border: 1px solid #58a6ff !important;
    color: #58a6ff !important;
}
</style>
"""
