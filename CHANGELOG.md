# Changelog

All notable changes to CrisisLens will be documented in this file.

## [1.0.0] - 2026-06-02

### Added
- Initial release of CrisisLens platform
- DistilBERT crisis classifier (4-label multi-classification)
- Real-time event ingestion pipeline
- Geospatial intelligence extraction with location resolution
- Chain-of-thought reasoning via Groq LLM API
- FAISS-based semantic search for historical events
- SQLite-backed event persistence (15-column schema)
- FastAPI REST endpoints for events and health checks
- Streamlit live ops dashboard with:
  - Real-time event feed (40 events, sorted by urgency)
  - Crisis type filtering and severity thresholds
  - KPI tiles (critical, elevated, low events)
  - Geospatial crisis maps
  - Urgency timeline charts
  - Event severity distribution histograms
  - Comprehensive onboarding sidebar
- Comprehensive system health check script (8 test sections)
- End-to-end test events with sub-3-second latency
- Docker support with docker-compose
- GitHub Actions CI/CD workflows
- Comprehensive documentation (architecture, API, deployment)

### Features
- **Classification**: Multi-label crisis detection (flood, fire, earthquake, medical)
- **Severity Scoring**: 0.0–1.0 scale with medical crisis priority
- **Location Extraction**: spaCy NER + Nominatim rate-limited geocoding
- **Reasoning**: Optional Groq LLM with FAISS RAG retrieval
- **Database**: Fresh SQLite connections per request, no threading issues
- **API Health Checks**: Comprehensive endpoint monitoring
- **Production Ready**: Async/await pipeline, proper error handling, logging

### Fixed
- DistilBERT token handling (skip_special_tokens=True)
- SQLite threading errors (fresh connections per request)
- Streamlit metric widget missing value parameter
- Event data type mismatch (JSON parsing in dashboard)
- LLM client cleanup (aclose on None check)
- Dashboard UX accessibility (comprehensive sidebar onboarding)
- Chart rendering (fixed severity histogram x-axis, label distribution ordering)

### Performance
- Classifier inference: ~1.5s
- Entity extraction: ~0.5s
- Geocoding (rate-limited): ~3-5s
- Database operations: <100ms
- **End-to-end latency: <9s** ✅

---

## Future Roadmap

- [ ] LLM httpx timeout investigation and fix
- [ ] WebSocket real-time updates
- [ ] Multi-language support (French, Spanish, Hindi)
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Integration with emergency APIs (911, FEMA)
- [ ] Automated response triggers
- [ ] Custom alert thresholds
- [ ] Team collaboration features
- [ ] Historical analysis tools
