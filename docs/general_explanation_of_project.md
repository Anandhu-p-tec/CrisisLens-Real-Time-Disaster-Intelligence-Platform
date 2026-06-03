# CrisisLens — Real-Time Disaster Intelligence Platform

> An AI system that monitors live social media streams during natural disasters, classifies crisis signals (flood, fire, earthquake, medical emergency), extracts structured data (location, severity, need type), and routes actionable intelligence to a live ops dashboard — with an LLM-powered reasoning layer that explains WHY something is a crisis signal and how confident it is.

---

## What I rejected before designing this

~~PDF chatbot~~ ~~RAG Q&A bot~~ ~~LangChain agent tutorial~~ ~~Resume screener~~ ~~Stock price predictor~~ ~~Sentiment analyser~~ ~~Image captioner~~ ~~Multi-agent debater~~ ~~Customer support chatbot~~ ~~Spam classifier~~

---

## Why this is different

No fresher has this. It combines real-time streaming, NLP classification, geospatial extraction, multi-label ML, LLM reasoning, and a live ops dashboard into one coherent system with a real-world humanitarian purpose. Interviewers at Flipkart, Razorpay, Sarvam AI, and IBM will remember this conversation for weeks.

---

## The Real Problem It Solves

During disasters, critical information is buried in noise.

When the 2023 Turkey earthquake or 2024 Wayanad floods hit, thousands of people posted "trapped on 3rd floor, need rescue, Meppadi" on social media — but emergency responders had no system to parse this in real-time. Traditional monitoring is keyword-search only. CrisisLens turns this into structured, prioritized, location-tagged intelligence with an LLM explaining the reasoning chain.

---

## Full System Architecture

### Data Ingestion — Live stream simulator
- Twitter/X API v2 or Bluesky API
- Reddit PRAW (disaster subreddits)
- Kafka / Redis Streams queue
- Synthetic data generator for demo

### ML Classification — Crisis signal detector
- Fine-tuned BERT / DistilBERT
- Multi-label: flood, fire, quake, medical
- Severity scorer (0–1 urgency)
- scikit-learn + HuggingFace Transformers

### NLP Extraction — Entity & location extractor
- spaCy NER (location, org, person)
- Geopy / Google Maps API geocoding
- SQLite + PostGIS storage
- Structured JSON output per event

### LLM Reasoning — Explainability layer
- Groq API (llama-3.1-8b-instant)
- RAG over past crisis patterns (FAISS)
- Chain-of-thought: WHY is this urgent?
- Confidence score + human override flag

### API + Storage — Backend
- FastAPI (REST + WebSocket)
- SQLite (events DB, timeseries)
- Pandas aggregations
- Docker + docker-compose

### Live Dashboard — Ops frontend
- Streamlit (live map + feed)
- Folium / Plotly (geo heatmap)
- WebSocket real-time updates
- Crisis cards with LLM explanation

---

## Data Flow — Step by Step

```
01 Raw tweet / post arrives
      ↓
02 BERT classifies crisis type + severity
      ↓
03 spaCy extracts location + needs
      ↓
04 Gemini reasons WHY + flags confidence
      ↓
05 Dashboard pins event on live map
```

---

## Every Skill Interviewers Test — Covered

| Category | What it covers |
|---|---|
| Classical ML | BERT fine-tuning, multi-label classification, F1/precision/recall |
| NLP | NER, spaCy pipelines, text preprocessing, tokenization |
| GenAI / LLM | Groq API (llama-3.1-8b-instant), chain-of-thought prompting, RAG with FAISS |
| Data engineering | Streaming pipeline, Kafka/Redis, Pandas, SQL queries |
| MLOps | Model evaluation, threshold tuning, batch vs stream inference |
| Production | FastAPI + WebSocket, Docker Compose, REST API design |
| Visualisation | Plotly, Folium geo heatmaps, live Streamlit dashboard |
| System design | Real-time pipeline, latency vs throughput tradeoffs, queue design |
| Domain depth | Crisis informatics, humanitarian AI — rare for freshers |

---

## The "Wow Factors" That Make Interviewers Stop Scrolling

### LLM Explainability — not just classification

Most projects classify and stop. CrisisLens asks Gemini: *"This post says 'water level rising, kids trapped'. Here are 3 similar past crisis posts. Explain in 2 sentences why this is classified as high-severity flood, and what the response team should do first."* — This is the rare explainable AI + RAG combo. No other fresher portfolio has this.

### Geo-Intelligence — location is everything in crisis response

The system resolves vague location mentions ("near the old bridge in Thrissur") to coordinates using spaCy NER → Geopy geocoding → Folium map pin. This is a hard NLP problem that sounds simple. It demonstrates understanding of real-world messiness vs clean benchmark datasets.

### Real-Time Streaming with Latency Benchmarking

You can show a chart: "Average end-to-end latency from post ingestion to dashboard display: 1.2 seconds." Quantified metrics on a real-time system is something 99% of fresher portfolios never have. It turns your README into something that reads like a systems paper.

---

## Build Roadmap — Realistic for a Final Year Student

### Week 1–2 (~20 hrs) — Dataset + baseline classifier
Use CrisisNLP / HumAID public dataset (real disaster tweets, already labelled). Fine-tune DistilBERT on HuggingFace. Get F1 > 0.82 baseline. Write evaluation notebook with confusion matrix + per-class scores.

### Week 3 (~15 hrs) — NER + location extraction pipeline
Train spaCy NER on crisis text. Add Geopy geocoding. Store structured events (type, location lat/lng, severity, raw text) in SQLite. Write SQL queries for aggregation (events by type, by hour, by region).

### Week 4 (~12 hrs) — LLM reasoning layer + RAG
Index past crisis events in FAISS. On each new high-severity event, retrieve 3 similar past events and send to Gemini with a structured prompt. Parse structured JSON response (reasoning, confidence, recommended action).

### Week 5 (~15 hrs) — FastAPI backend + streaming simulator
Build FastAPI with WebSocket endpoint. Build a tweet simulator that replays the dataset at 10x speed so you can demo live ingestion without needing real API access. Docker Compose ties everything together.

### Week 6 (~15 hrs) — Streamlit ops dashboard
Live event feed (WebSocket), Folium geo heatmap, severity histogram, crisis card UI showing LLM reasoning. Record a 2-minute Loom demo video. Add architecture diagram to README. Deploy to Hugging Face Spaces.

**Total: ~75–80 hours across 6 weeks**

---

## How This Plays Out in the Interview

**"Walk me through your most interesting project."**

You explain a real-world problem (disaster response), a full ML pipeline, a production system design, and an ethical AI angle (explainability + human override). The interviewer is now asking questions, not you.

**"How did you handle noisy, unstructured social media text?"**

You talk about tweet preprocessing, handling code-switching (Hindi-English mix), threshold tuning, and why you chose DistilBERT over a larger model for latency reasons. This is a senior-level discussion from a fresher.

**"Why does the LLM sometimes disagree with the classifier?"**

You explain the human-override flag design — when confidence < 0.6, the LLM reasoning is shown to the operator who makes the final call. This is responsible AI design. Most freshers have never thought about this.

---

## The Kerala Connection — Your Story

You're from Kerala. Wayanad floods happened. You can say in your resume:

> *"Built to address the information chaos during the 2024 Wayanad disaster."*

That one sentence makes it personal and memorable instead of academic.

---

## The Dataset — Start on Day 1

**CrisisNLP** and **HumAID** are public, real disaster tweet datasets with labels — you don't have to scrape anything or invent data. This means you can start building immediately.

- HumAID: https://crisisnlp.qcri.org/humaid_dataset
- CrisisNLP: https://crisisnlp.qcri.org

---

## Full Tech Stack Summary

```
ML / NLP       : HuggingFace Transformers, DistilBERT, spaCy, scikit-learn
LLM / RAG      : Groq API (llama-3.1-8b-instant), FAISS, LangChain (optional)
Streaming      : Kafka / Redis Streams
Backend        : FastAPI, WebSocket, SQLite, Pandas
Frontend       : Streamlit, Folium, Plotly
DevOps         : Docker, docker-compose
Deployment     : Hugging Face Spaces
Geocoding      : Geopy / Google Maps API
```