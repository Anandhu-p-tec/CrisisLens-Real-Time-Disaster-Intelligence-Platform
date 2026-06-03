# CrisisLens — Architecture

**Version**: 1.0.0  
**Stack**: Python 3.11 · FastAPI · HuggingFace Transformers · spaCy · FAISS · Groq API (llama-3.1-8b-instant) · Streamlit · SQLite · Docker

---

## Guiding Principles

1. **Separation of concerns** — ingestion, classification, extraction, reasoning, storage, and presentation are independent layers. No layer reaches into another's internals.
2. **Typed contracts** — all data crossing a layer boundary is a Pydantic model. No raw dicts.
3. **Configuration at the edge** — all secrets and tunable parameters live in environment variables loaded at startup. Nothing is hardcoded.
4. **Async by default** — the pipeline is fully async from ingestion to WebSocket push. Blocking operations (model inference) run in a thread pool.
5. **Observable** — every stage emits structured logs. Latency from ingestion to dashboard is measurable and benchmarkable.

---

## Repository Layout

```
crisislens/
│
├── app/                          # Core application package
│   ├── core/
│   │   ├── config.py             # Pydantic Settings — all env vars loaded here
│   │   ├── logging.py            # Structured logging configuration
│   │   └── exceptions.py         # Domain exception hierarchy
│   │
│   ├── ingestion/
│   │   ├── stream_simulator.py   # Replays HumAID dataset at configurable speed
│   │   └── schema.py             # RawPostSchema — the ingestion contract
│   │
│   ├── classification/
│   │   ├── classifier.py         # DistilBERT multi-label inference
│   │   ├── severity.py           # Urgency score (0.0–1.0) from classifier logits
│   │   └── schema.py             # ClassificationResultSchema
│   │
│   ├── extraction/
│   │   ├── ner_pipeline.py       # spaCy NER — location, org, person extraction
│   │   ├── geocoder.py           # Geopy → (lat, lng) resolution
│   │   └── schema.py             # ExtractionResultSchema
│   │
│   ├── reasoning/
│   │   ├── llm_service.py        # Groq API (llama-3.1-8b-instant) client — all LLM calls centralised here
│   │   ├── rag_retriever.py      # FAISS index — similar past events retrieval
│   │   ├── prompt_builder.py     # Chain-of-thought prompt assembly
│   │   └── schema.py             # ReasoningResultSchema
│   │
│   ├── pipeline/
│   │   └── processor.py          # Orchestrates classifier → extractor → reasoner
│   │
│   ├── repository/
│   │   ├── database.py           # SQLite connection, table creation
│   │   ├── events.py             # CRUD for crisis events
│   │   └── schema.py             # CrisisEventRecord — the DB row model
│   │
│   ├── api/
│   │   ├── main.py               # FastAPI app factory
│   │   ├── routers/
│   │   │   ├── events.py         # GET /events, GET /events/{id}
│   │   │   ├── stream.py         # WebSocket /ws/feed
│   │   │   └── health.py         # GET /health
│   │   └── schema.py             # API response envelope schemas
│   │
│   └── dashboard/
│       └── app.py                # Streamlit entry point
│
├── models/                       # Saved model weights (gitignored)
│   └── crisis_classifier/        # HuggingFace save_pretrained output
│
├── data/
│   ├── raw/                      # Downloaded HumAID / CrisisNLP CSVs (gitignored)
│   └── processed/                # Tokenised, split datasets (gitignored)
│
├── notebooks/
│   ├── training.ipynb            # DistilBERT fine-tuning + evaluation
│   └── ner_evaluation.ipynb      # spaCy NER evaluation on crisis text
│
├── scripts/
│   ├── train_classifier.py       # CLI: fine-tune and save the classifier
│   ├── build_faiss_index.py      # CLI: build FAISS index from events DB
│   └── evaluate_pipeline.py     # CLI: end-to-end latency benchmark
│
├── tests/
│   ├── test_classifier.py
│   ├── test_ner_pipeline.py
│   ├── test_geocoder.py
│   ├── test_llm_service.py
│   └── test_pipeline.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## Data Flow

```
Stream Simulator
      │
      │  RawPostSchema
      ▼
 Classifier  ──────────────────────────────────────────────────────────┐
      │                                                                 │
      │  ClassificationResultSchema                                     │
      ▼                                                                 │
 NER + Geocoder                                                         │
      │                                                                 │
      │  ExtractionResultSchema                                         │
      ▼                                                                 │
 LLM Reasoner  (only when severity ≥ 0.6)                              │
      │                                                                 │
      │  ReasoningResultSchema                                          │
      ▼                                                                 │
 Repository  ──── SQLite ─────────────────────────────────────────────┤
      │                                                                 │
      ▼                                                                 │
 FastAPI WebSocket ──── Streamlit Dashboard ◄──── REST /events ────────┘
```

---

## Layer Contracts

### `RawPostSchema`
```
post_id       str        Platform-native ID
text          str        Raw post text
platform      str        "twitter" | "reddit" | "simulator"
created_at    datetime   UTC
```

### `ClassificationResultSchema`
```
post_id       str
labels        list[str]  Subset of: flood, fire, earthquake, medical
severity      float      0.0 – 1.0  (urgency score)
confidence    float      Max label probability
raw_logits    list[float]
```

### `ExtractionResultSchema`
```
post_id       str
locations     list[str]  Raw location strings from NER
coordinates   tuple[float, float] | None   (lat, lng) after geocoding
needs         list[str]  Extracted need types (rescue, medical, food, …)
entities      dict       {person: [], org: []}
```

### `ReasoningResultSchema`
```
post_id           str
reasoning         str        LLM chain-of-thought (2–3 sentences)
recommended_action str
confidence_level  str        "high" | "medium" | "low"
human_override    bool       True when LLM confidence < 0.6
similar_events    list[str]  Post IDs of retrieved FAISS neighbours
```

### `CrisisEventRecord` (DB row)
```
id                int        Auto PK
post_id           str        Unique
text              str
platform          str
created_at        datetime
labels            str        JSON array
severity          float
confidence        float
lat               float | None
lng               float | None
location_raw      str | None
reasoning         str | None
recommended_action str | None
human_override    bool
indexed_at        datetime   When the event entered the DB
```

---

## Classification Architecture

**Model**: `distilbert-base-uncased` fine-tuned on HumAID (8 classes → collapsed to 4 macro-labels)

**Macro-label mapping**:
| HumAID label | Macro-label |
|---|---|
| `flooding`, `infrastructure_and_utility_damage` | `flood` |
| `fires` | `fire` |
| `earthquake` | `earthquake` |
| `injured_or_dead_people`, `rescue_volunteering_or_donation_effort` | `medical` |
| `caution_and_advice`, `not_humanitarian` | — (filtered out) |

**Severity scoring**: derived from the max sigmoid probability across active labels, scaled by a hand-tuned urgency weight per label type (medical > earthquake > flood > fire for default config).

**Inference mode**: runs in a `ThreadPoolExecutor` (1 worker) to not block the async event loop.

**Threshold**: labels with sigmoid probability ≥ 0.45 are activated. Configurable via `CLASSIFIER_THRESHOLD` env var.

---

## LLM Reasoning Layer

**Model**: Claude claude-sonnet-4-20250514 via Anthropic SDK

**Trigger condition**: `severity ≥ 0.6` (configurable via `LLM_SEVERITY_THRESHOLD`)

**RAG context**: FAISS L2 index over sentence embeddings of stored events. At inference time, 3 nearest neighbours are retrieved and injected into the prompt.

**Prompt structure**:
```
System: You are a crisis intelligence analyst. Respond in JSON only.
        Schema: {reasoning: str, recommended_action: str, confidence_level: "high"|"medium"|"low"}

User: New post: "{text}"
      Classification: {labels}, severity {severity:.2f}
      Location resolved: {coordinates}

      Similar past events:
      1. "{past_text_1}" → {past_labels_1}
      2. "{past_text_2}" → {past_labels_2}
      3. "{past_text_3}" → {past_labels_3}

      In 2 sentences explain why this is a {labels} event at this severity.
      Then state the single most important first action for a response team.
```

**Human override**: if `confidence_level == "low"`, `human_override` is set to `True` in the DB record and the dashboard renders a yellow flag on the crisis card.

---

## API Surface

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/events` | Paginated event list. Query params: `label`, `min_severity`, `platform`, `limit`, `offset` |
| `GET` | `/events/{id}` | Single event with full reasoning |
| `WebSocket` | `/ws/feed` | Real-time push of new events as they are processed |

All responses wrapped in:
```json
{
  "data": {...},
  "meta": {"timestamp": "...", "version": "1.0.0"}
}
```

---

## Storage

**SQLite** (single-file, zero-ops) — appropriate for this project's throughput (< 50 events/sec in demo).

**FAISS** — `IndexFlatL2` over 768-dimensional `all-MiniLM-L6-v2` embeddings. Persisted to `data/faiss.index`. Rebuilt by `scripts/build_faiss_index.py` whenever the events DB grows significantly.

---

## Configuration Reference

All loaded from environment via `app/core/config.py` (Pydantic Settings):

```
ANTHROPIC_API_KEY          Required
CLASSIFIER_MODEL_PATH      Default: models/crisis_classifier
CLASSIFIER_THRESHOLD       Default: 0.45
LLM_SEVERITY_THRESHOLD     Default: 0.6
GEOCODER_USER_AGENT        Required (Nominatim ToS)
FAISS_INDEX_PATH           Default: data/faiss.index
DATABASE_URL               Default: data/crisislens.db
SIMULATOR_SPEED_FACTOR     Default: 10  (10× replay speed)
LOG_LEVEL                  Default: INFO
```

---

## Docker

```yaml
# docker-compose.yml (overview)
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    volumes:
      - ./models:/app/models
      - ./data:/app/data

  dashboard:
    build: .
    command: streamlit run app/dashboard/app.py
    ports: ["8501:8501"]
    env_file: .env
    depends_on: [api]
```

Single `Dockerfile`, two service entries. No separate images.

---

## Development Workflow

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Train classifier (requires data/raw/ populated)
python scripts/train_classifier.py

# 3. Build FAISS index (after training)
python scripts/build_faiss_index.py

# 4. Start everything
docker compose up

# 5. Run tests
pytest tests/ -v
```

---

## What Is Intentionally Out of Scope

- **Real Twitter/X API**: replaced by the stream simulator for demo purposes. API integration is a drop-in swap — the simulator emits the same `RawPostSchema`.
- **Kafka / Redis**: out of scope for a single-machine demo. The simulator writes directly to the pipeline's async queue. Architecture is designed so a Kafka consumer can replace it without touching downstream code.
- **Authentication**: no auth on the API. Not appropriate for a portfolio demo adding complexity with no interviewer value.
- **Alembic migrations**: SQLite schema created at startup via `CREATE TABLE IF NOT EXISTS`. Migrations are overkill at this scale.