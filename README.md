![CrisisLens](https://img.shields.io/badge/⬡-CrisisLens-58a6ff?style=flat-square&labelColor=0d1117&color=58a6ff)

**Real-Time Disaster Intelligence Platform**

AI-powered crisis detection that monitors social media during disasters,
classifies crisis signals, extracts geospatial intelligence, and routes
actionable alerts to emergency responders — in under 3 seconds.

![](https://img.shields.io/badge/Python-3.11+-58a6ff?style=flat-square&labelColor=0d1117)
![](https://img.shields.io/badge/DistilBERT-Fine--tuned-3fb950?style=flat-square&labelColor=0d1117)
![](https://img.shields.io/badge/Groq-llama--3.1--8b-d29922?style=flat-square&labelColor=0d1117)
![](https://img.shields.io/badge/Tests-56%2F56%20passing-3fb950?style=flat-square&labelColor=0d1117)
![](https://img.shields.io/badge/Latency-2.22s%20e2e-f85149?style=flat-square&labelColor=0d1117)
![](https://img.shields.io/badge/License-Apache%202.0-8b949e?style=flat-square&labelColor=0d1117)

---

## The Problem

During the 2024 Wayanad floods, thousands of people posted
`"trapped on 3rd floor, need rescue, Meppadi"` on social media.
Emergency responders had no system to parse this in real time.
CrisisLens turns this unstructured noise into structured,
prioritized, location-tagged intelligence — with an LLM
explaining the reasoning chain behind every classification.

---

## Pipeline

```
Social Media Post
│
▼
[DistilBERT Classifier]  →  crisis type + severity score (0–1)
│
▼
[spaCy NER]  →  locations, organizations, persons
│
▼
[Nominatim Geocoder]  →  (lat, lng) coordinates
│
▼
[Groq LLM + FAISS RAG]  →  chain-of-thought explanation
│                      + recommended action
▼
[SQLite → FastAPI → WebSocket]
│
▼
[Streamlit Ops Dashboard]  →  live map · KPIs · event feed
```

**End-to-end latency: 2.22 seconds · 56/56 system checks passing**

---

## What It Detects

| Label | Description | Urgency Weight |
|---|---|---|
| `medical` | Injuries, casualties, urgent aid needed | 1.0 |
| `earthquake` | Structural damage, trapped survivors | 0.9 |
| `flood` | Rising water, displaced families | 0.8 |
| `fire` | Wildfires, building fires, evacuations | 0.75 |

Severity is computed as `max(sigmoid(logit) × urgency_weight)` 
across active labels. Events above `0.6` trigger the LLM 
reasoning layer.

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/Anandhu-p-tec/CrisisLens-Real-Time-Disaster-Intelligence-Platform.git
cd CrisisLens-Real-Time-Disaster-Intelligence-Platform
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
# source .venv/bin/activate         # macOS/Linux
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Add your Groq API key (free at console.groq.com)

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Prepare dataset and train classifier
python scripts/download_data.py
python scripts/prepare_dataset.py
# Open notebooks/training.ipynb and run all cells
# (Use Google Colab with T4 GPU for ~15 min training)
```

---

## Running

Open three terminals:

```
# Terminal 1 — API
python scripts/start_api.py
# → http://localhost:8000

# Terminal 2 — Dashboard  
python scripts/start_dashboard.py
# → http://localhost:8501

# Terminal 3 — Ingest events
python scripts/ingest.py --events 100 --speed 3.0
```

---

## System Check

```
python scripts/test_system.py
```

```
============================================================
CRISISLENS — FULL SYSTEM CHECK
============================================================
[1/8] ENVIRONMENT      ✅ all checks passed
[2/8] IMPORTS          ✅ all 17 modules import cleanly
[3/8] CLASSIFIER       ✅ severity=0.733 · labels=['flood','medical']
[4/8] NER PIPELINE     ✅ locations=['Wayanad','Kerala','Meppadi']
[5/8] SEVERITY SCORER  ✅ medical(0.900) > fire(0.675) ✓
[6/8] DATABASE         ✅ insert + fetch verified
[7/8] API ENDPOINTS    ✅ /health · /events · filters
[8/8] END-TO-END       ✅ 2.22s latency · pipeline verified
────────────────────────────────────────────────────────────
  Passed  : 56/56   Failed: 0   Warnings: 0
  🎉 ALL CHECKS PASSED — system is demo-ready
────────────────────────────────────────────────────────────
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/events` | All events — filter by `label`, `min_severity`, `platform` |
| `GET` | `/events/{id}` | Single event with full LLM reasoning |
| `WS` | `/ws/feed` | Real-time WebSocket push |

```
# Example: fetch critical flood events
curl "http://localhost:8000/events?label=flood&min_severity=0.7&limit=10"
```

---

## Project Structure

```
crisislens/
├── app/
│   ├── core/            # config · logging · exceptions
│   ├── ingestion/       # stream simulator · RawPostSchema
│   ├── classification/  # DistilBERT · severity scorer
│   ├── extraction/      # spaCy NER · Nominatim geocoder
│   ├── reasoning/       # Groq LLM · FAISS RAG · prompt builder
│   ├── repository/      # SQLite · async CRUD
│   ├── pipeline/        # CrisisProcessor orchestrator
│   ├── api/             # FastAPI · WebSocket
│   └── dashboard/       # Streamlit · Folium · Plotly
├── scripts/
│   ├── start_api.py         # launch API
│   ├── start_dashboard.py   # launch dashboard
│   ├── ingest.py            # run event simulation
│   ├── test_system.py       # 56-check health report
│   ├── evaluate_pipeline.py # latency benchmark
│   ├── train_classifier.py  # model training CLI
│   └── build_faiss_index.py # rebuild vector index
├── notebooks/
│   └── training.ipynb   # DistilBERT fine-tuning + evaluation
├── tests/               # pytest unit + integration tests
├── docs/                # architecture · design decisions
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Stack

| Layer | Technology |
|-------|-----------|
| ML Classification | HuggingFace Transformers · DistilBERT |
| NLP | spaCy en_core_web_sm |
| LLM | Groq API · llama-3.1-8b-instant (free) |
| Vector Search | FAISS IndexFlatL2 · sentence-transformers |
| Geocoding | Geopy · Nominatim (OpenStreetMap) |
| Backend | FastAPI · Uvicorn · WebSocket |
| Database | SQLite · aiosqlite |
| Dashboard | Streamlit · Folium · Plotly |
| Async | asyncio · ThreadPoolExecutor |
| DevOps | Docker · docker-compose |

---

## Design Principles

Every layer communicates through typed Pydantic schemas —
nothing crosses a module boundary as a raw dict. The pipeline
is fully async from ingestion to WebSocket push. Blocking
operations (model inference, geocoding) run in thread pool
executors to avoid stalling the event loop. All configuration
lives in `.env` — nothing is hardcoded.

---

## Dataset

Trained on **HumAID** crisis tweet dataset. Labels collapsed
to 4 macro-classes. Training split: 70/15/15 stratified.

| Label | Train samples |
|-------|--------------|
| medical | 2,784 |
| flood | 1,898 |
| fire | 667 |
| earthquake | 658 |

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

<div align="center">
<sub>Built to address the information chaos during the 2024 Wayanad disaster.</sub>
</div>
