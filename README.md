<div align="center">

<br/>

```
 ██████╗██████╗ ██╗███████╗██╗███████╗██╗     ███████╗███╗   ██╗███████╗
██╔════╝██╔══██╗██║██╔════╝██║██╔════╝██║     ██╔════╝████╗  ██║██╔════╝
██║     ██████╔╝██║███████╗██║███████╗██║     █████╗  ██╔██╗ ██║███████╗
██║     ██╔══██╗██║╚════██║██║╚════██║██║     ██╔══╝  ██║╚██╗██║╚════██║
╚██████╗██║  ██║██║███████║██║███████║███████╗███████╗██║ ╚████║███████║
 ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝
```

**Real-Time Disaster Intelligence Platform**

*AI that turns social media chaos into structured crisis intelligence — in 2.22 seconds.*

<br/>

![Python](https://img.shields.io/badge/Python-3.11+-58a6ff?style=for-the-badge&labelColor=0d1117&logo=python&logoColor=58a6ff)
![DistilBERT](https://img.shields.io/badge/DistilBERT-Fine--tuned-3fb950?style=for-the-badge&labelColor=0d1117&logo=huggingface&logoColor=3fb950)
![Groq](https://img.shields.io/badge/Groq-llama--3.1--8b-d29922?style=for-the-badge&labelColor=0d1117)
![Tests](https://img.shields.io/badge/Tests-56%2F56_passing-3fb950?style=for-the-badge&labelColor=0d1117)
![Latency](https://img.shields.io/badge/Latency-2.22s_e2e-f85149?style=for-the-badge&labelColor=0d1117)
![License](https://img.shields.io/badge/License-Apache_2.0-8b949e?style=for-the-badge&labelColor=0d1117)

<br/>

</div>

---

## ⚡ The Problem

> *During the 2024 Wayanad floods, thousands of people posted*
> *`"trapped on 3rd floor, need rescue, Meppadi"` on social media.*
> *Emergency responders had no system to parse this in real time.*

Traditional disaster monitoring is keyword search. **CrisisLens** is different — it classifies crisis type, scores urgency, resolves locations to coordinates, and asks an LLM *why* it flagged the event, all within 3 seconds of ingestion.

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   "flooding in Wayanad, people trapped on rooftops, need rescue"   │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
              ┌────────────────▼─────────────────┐
              │        DistilBERT Classifier      │
              │   fine-tuned on 6,007 HumAID      │
              │   crisis tweets                   │
              │                                   │
              │   labels  →  flood · medical      │
              │   severity →  0.73 / 1.00         │
              └────────────────┬─────────────────┘
                               │
              ┌────────────────▼─────────────────┐
              │         spaCy NER Pipeline        │
              │                                   │
              │   locations → Wayanad · Kerala    │
              │   needs     → rescue · trapped    │
              │   coords    → (11.68, 76.13)      │
              └────────────────┬─────────────────┘
                               │
              ┌────────────────▼─────────────────┐
              │      Groq LLM + FAISS RAG         │
              │                                   │
              │   retrieves 3 similar past events │
              │   explains WHY this is critical   │
              │   recommends first response action│
              └────────────────┬─────────────────┘
                               │
              ┌────────────────▼─────────────────┐
              │   SQLite → FastAPI → WebSocket    │
              │         → Streamlit Dashboard     │
              │                                   │
              │   live map · KPIs · event feed    │
              │   auto-refresh every 8 seconds    │
              └──────────────────────────────────┘
```

---

## 🎯 What It Detects

<table>
<tr>
<td align="center"><b>🌊 FLOOD</b></td>
<td>Rising water levels · submerged roads · displaced families</td>
<td align="center"><code>weight: 0.80</code></td>
</tr>
<tr>
<td align="center"><b>🔥 FIRE</b></td>
<td>Wildfires · building fires · evacuation orders</td>
<td align="center"><code>weight: 0.75</code></td>
</tr>
<tr>
<td align="center"><b>🏔️ EARTHQUAKE</b></td>
<td>Structural damage · trapped survivors · aftershocks</td>
<td align="center"><code>weight: 0.90</code></td>
</tr>
<tr>
<td align="center"><b>🏥 MEDICAL</b></td>
<td>Injuries · mass casualties · urgent medical aid</td>
<td align="center"><code>weight: 1.00</code></td>
</tr>
</table>

> Severity = `max(sigmoid(logit) × urgency_weight)` across active labels.
> Events above **0.6** trigger the LLM reasoning layer.

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Anandhu-p-tec/CrisisLens-Real-Time-Disaster-Intelligence-Platform.git
cd CrisisLens-Real-Time-Disaster-Intelligence-Platform

# 2. Install
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -e ".[dev]"
python -m spacy download en_core_web_sm

# 3. Configure
cp .env.example .env
# → Add your free Groq API key from console.groq.com

# 4. Prepare data + train
python scripts/download_data.py
python scripts/prepare_dataset.py
# Open notebooks/training.ipynb in Google Colab (T4 GPU, ~15 min)
```

---

## 🖥️ Running

```bash
# Terminal 1 — API backend
python scripts/start_api.py
# → http://localhost:8000

# Terminal 2 — Ops dashboard
python scripts/start_dashboard.py
# → http://localhost:8501

# Terminal 3 — Feed events into the system
python scripts/ingest.py --events 100 --speed 3.0
```

Open **http://localhost:8501** — watch events populate the live map in real time.

---

## ✅ System Check

```bash
python scripts/test_system.py
```

```
============================================================
  CRISISLENS — FULL SYSTEM CHECK
============================================================

  [1/8] ENVIRONMENT      ✅  GROQ key · model path · dataset
  [2/8] IMPORTS          ✅  17 modules import cleanly
  [3/8] CLASSIFIER       ✅  severity=0.733 · ['flood','medical']
  [4/8] NER PIPELINE     ✅  ['Wayanad', 'Kerala', 'Meppadi']
  [5/8] SEVERITY SCORER  ✅  medical(0.900) > fire(0.675)
  [6/8] DATABASE         ✅  insert + fetch verified
  [7/8] API ENDPOINTS    ✅  /health · /events · filters
  [8/8] END-TO-END       ✅  2.22s · pipeline complete

────────────────────────────────────────────────────────────
  Passed: 56/56    Failed: 0    Warnings: 0
  🎉 ALL CHECKS PASSED — system is demo-ready
────────────────────────────────────────────────────────────
```

---

## 📡 API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/events` | All events — filter by `label`, `min_severity`, `platform` |
| `GET` | `/events/{id}` | Single event with full LLM reasoning |
| `WS` | `/ws/feed` | Real-time WebSocket push |

```bash
# Critical flood events only
curl "http://localhost:8000/events?label=flood&min_severity=0.7&limit=10"
```

---

## 📁 Structure

```
crisislens/
│
├── app/
│   ├── core/            ← config · logging · exceptions
│   ├── ingestion/       ← stream simulator · RawPostSchema
│   ├── classification/  ← DistilBERT · severity scorer
│   ├── extraction/      ← spaCy NER · Nominatim geocoder
│   ├── reasoning/       ← Groq LLM · FAISS RAG · prompts
│   ├── repository/      ← SQLite · async CRUD
│   ├── pipeline/        ← CrisisProcessor orchestrator
│   ├── api/             ← FastAPI · WebSocket
│   └── dashboard/       ← Streamlit · Folium · Plotly
│
├── scripts/
│   ├── start_api.py          ← launch API server
│   ├── start_dashboard.py    ← launch dashboard
│   ├── ingest.py             ← CLI event ingestion
│   ├── test_system.py        ← 56-check health report
│   ├── evaluate_pipeline.py  ← latency benchmark
│   ├── train_classifier.py   ← model training CLI
│   └── build_faiss_index.py  ← rebuild vector index
│
├── notebooks/
│   └── training.ipynb   ← DistilBERT fine-tuning + evaluation
│
├── tests/               ← pytest unit + integration tests
├── docs/                ← architecture · design decisions
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## 🔬 Performance

| Stage | Latency | Notes |
|-------|---------|-------|
| DistilBERT inference | ~0.8s | ThreadPoolExecutor, no event loop blocking |
| spaCy NER | ~0.05s | Synchronous, sub-100ms |
| Nominatim geocoding | ~1.1s | Rate-limited per ToS |
| Groq LLM reasoning | ~2–3s | Only triggers at severity ≥ 0.6 |
| SQLite write | <50ms | aiosqlite async |
| **End-to-end (no LLM)** | **2.22s** | **Verified benchmark** |

---

## 🛠️ Stack

| Layer | Technology |
|-------|------------|
| ML Classification | HuggingFace Transformers · DistilBERT |
| NLP | spaCy `en_core_web_sm` |
| LLM | Groq API · `llama-3.1-8b-instant` (free tier) |
| Vector Search | FAISS `IndexFlatL2` · `sentence-transformers` |
| Geocoding | Geopy · Nominatim (OpenStreetMap) |
| Backend | FastAPI · Uvicorn · WebSocket |
| Database | SQLite · aiosqlite |
| Dashboard | Streamlit · Folium · Plotly |
| Async | asyncio · ThreadPoolExecutor |
| DevOps | Docker · docker-compose |

---

## 🏗️ Design Principles

```
Separation of concerns  →  each layer owns one responsibility
Typed contracts         →  Pydantic schemas at every boundary, no raw dicts
Config at the edge      →  all secrets in .env, nothing hardcoded
Async by default        →  non-blocking from ingestion to WebSocket push
Observable              →  structured logs at every stage, latency measured
```

---

## 📊 Dataset

Trained on the **HumAID** crisis tweet corpus. Raw labels collapsed to 4 macro-classes for practical response utility.

| Label | Samples | Source HumAID Labels |
|-------|---------|----------------------|
| `medical` | 2,784 | injured_or_dead_people · rescue_volunteering |
| `flood` | 1,898 | flooding · infrastructure_damage |
| `fire` | 667 | fires |
| `earthquake` | 658 | earthquake |

Training split: **70% train · 15% val · 15% test** · stratified by label.

---

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE)

---

<div align="center">

<br/>

```
Built to address the information chaos during the 2024 Wayanad disaster.
```

<br/>

</div>
