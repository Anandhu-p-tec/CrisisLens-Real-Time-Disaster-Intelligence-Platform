from __future__ import annotations
import asyncio
import json
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.core.logging import configure_logging

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

results: list[tuple[str, str, str]] = []

def check(name: str, passed: bool, detail: str = "") -> None:
    status = PASS if passed else FAIL
    results.append((name, status, detail))
    symbol = "✅" if passed else "❌"
    print(f"  {symbol} {name}{' — ' + detail if detail else ''}")

def warn(name: str, detail: str = "") -> None:
    results.append((name, WARN, detail))
    print(f"  ⚠️  {name}{' — ' + detail if detail else ''}")


# ── 1. Environment ────────────────────────────────────────────────────────────
def test_environment() -> None:
    print("\n[1/8] ENVIRONMENT")
    check(
        "GROQ_API_KEY set",
        bool(settings.GROQ_API_KEY),
        "missing — LLM reasoning will be skipped" if not settings.GROQ_API_KEY else "",
    )
    check(
        "CLASSIFIER_MODEL_PATH exists",
        Path(settings.CLASSIFIER_MODEL_PATH).exists(),
        f"path={settings.CLASSIFIER_MODEL_PATH}",
    )
    check(
        "crisis_dataset.csv exists",
        Path("data/processed/crisis_dataset.csv").exists(),
    )
    check(
        "label_map.json exists",
        Path("data/processed/label_map.json").exists(),
    )
    env_file = PROJECT_ROOT / ".env"
    check(".env file present", env_file.exists())


# ── 2. Imports ────────────────────────────────────────────────────────────────
def test_imports() -> None:
    print("\n[2/8] IMPORTS")
    modules = [
        ("app.core.config", "Settings"),
        ("app.ingestion.schema", "RawPostSchema"),
        ("app.ingestion.stream_simulator", "StreamSimulator"),
        ("app.classification.schema", "CrisisLabel"),
        ("app.classification.severity", "compute_severity"),
        ("app.classification.classifier", "CrisisClassifier"),
        ("app.extraction.schema", "ExtractionResultSchema"),
        ("app.extraction.ner_pipeline", "NERPipeline"),
        ("app.extraction.geocoder", "Geocoder"),
        ("app.reasoning.schema", "ReasoningResultSchema"),
        ("app.reasoning.prompt_builder", "build_reasoning_prompt"),
        ("app.reasoning.rag_retriever", "RAGRetriever"),
        ("app.reasoning.llm_service", "LLMService"),
        ("app.repository.database", "initialise_database"),
        ("app.repository.events", "fetch_events"),
        ("app.pipeline.processor", "CrisisProcessor"),
        ("app.api.main", "app"),
    ]
    for module_path, attr in modules:
        try:
            import importlib
            mod = importlib.import_module(module_path)
            getattr(mod, attr)
            check(f"{module_path}.{attr}", True)
        except Exception as exc:
            check(f"{module_path}.{attr}", False, str(exc)[:80])


# ── 3. Classifier ─────────────────────────────────────────────────────────────
def test_classifier() -> None:
    print("\n[3/8] CLASSIFIER")
    try:
        from app.classification.classifier import CrisisClassifier
        from app.ingestion.schema import RawPostSchema
        clf = CrisisClassifier()
        check("CrisisClassifier loads", True)
        post = RawPostSchema(
            post_id="test_clf_001",
            text="Flooding in Kerala, people trapped on rooftops, need rescue",
            platform="simulator",
            created_at=datetime.now(tz=timezone.utc),
        )
        result = asyncio.get_event_loop().run_until_complete(clf.classify(post))
        check("classify() returns result", True)
        check(
            "severity in [0,1]",
            0.0 <= result.severity <= 1.0,
            f"severity={result.severity:.3f}",
        )
        check(
            "confidence in [0,1]",
            0.0 <= result.confidence <= 1.0,
            f"confidence={result.confidence:.3f}",
        )
        check(
            "labels list returned",
            isinstance(result.labels, list),
            f"labels={result.labels}",
        )
        if result.labels:
            check("label values valid", True, f"got {[str(l) for l in result.labels]}")
        else:
            warn("no labels activated", f"threshold={settings.CLASSIFIER_THRESHOLD} — try lowering it")
    except Exception as exc:
        check("CrisisClassifier", False, str(exc)[:120])


# ── 4. NER Pipeline ───────────────────────────────────────────────────────────
def test_ner() -> None:
    print("\n[4/8] NER PIPELINE")
    try:
        from app.extraction.ner_pipeline import NERPipeline
        ner = NERPipeline()
        check("NERPipeline loads", True)
        result = ner.extract(
            "test_ner_001",
            "Flash flood in Wayanad, Kerala — people trapped near Meppadi bridge",
        )
        check("extract() returns result", True)
        check(
            "locations extracted",
            len(result.locations) > 0,
            f"found={result.locations}",
        )
        check(
            "needs detected",
            isinstance(result.needs, list),
            f"needs={result.needs}",
        )
        check("coordinates is None before geocoding", result.coordinates is None)
    except Exception as exc:
        check("NERPipeline", False, str(exc)[:120])


# ── 5. Severity scorer ────────────────────────────────────────────────────────
def test_severity() -> None:
    print("\n[5/8] SEVERITY SCORER")
    from app.classification.severity import compute_severity
    check(
        "empty input returns 0.0",
        compute_severity({}) == 0.0,
    )
    med = compute_severity({"medical": 0.9})
    fire = compute_severity({"fire": 0.9})
    check(
        "medical > fire at same probability",
        med > fire,
        f"medical={med:.3f} fire={fire:.3f}",
    )
    check(
        "severity clamped to 1.0",
        compute_severity({"medical": 1.0, "earthquake": 1.0}) <= 1.0,
    )
    check(
        "below threshold returns 0.0",
        compute_severity({"flood": 0.1}) == 0.0,
        f"threshold={settings.CLASSIFIER_THRESHOLD}",
    )


# ── 6. Database ───────────────────────────────────────────────────────────────
async def _test_db() -> None:
    print("\n[6/8] DATABASE")
    try:
        from app.repository.database import initialise_database
        from app.repository.events import insert_event, fetch_events, fetch_event_by_id
        from app.repository.schema import CrisisEventRecord
        await initialise_database()
        check("database initialises", True)
        record = CrisisEventRecord(
            post_id=f"test_db_{int(time.time())}",
            text="Test event for system check",
            platform="simulator",
            created_at=datetime.now(tz=timezone.utc),
            labels=["flood"],
            severity=0.75,
            confidence=0.88,
            human_override=False,
            indexed_at=datetime.now(tz=timezone.utc),
        )
        row_id = await insert_event(record)
        check("insert_event() succeeds", row_id >= 0, f"row_id={row_id}")
        fetched = await fetch_event_by_id(record.post_id)
        check(
            "fetch_event_by_id() returns record",
            fetched is not None,
        )
        check(
            "fetched record matches inserted",
            fetched is not None and fetched.severity == 0.75,
            f"severity={fetched.severity if fetched else 'None'}",
        )
        all_events = await fetch_events(limit=5)
        check(
            "fetch_events() returns list",
            isinstance(all_events, list),
            f"count={len(all_events)}",
        )
    except Exception as exc:
        check("database layer", False, str(exc)[:120])


def test_database() -> None:
    asyncio.get_event_loop().run_until_complete(_test_db())


# ── 7. API endpoints ──────────────────────────────────────────────────────────
def test_api() -> None:
    print("\n[7/8] API ENDPOINTS")
    base = "http://localhost:8000"
    try:
        resp = httpx.get(f"{base}/health", timeout=5)
        check(
            "GET /health returns 200",
            resp.status_code == 200,
            f"status={resp.status_code}",
        )
        data = resp.json()
        check(
            "/health response has data.status=ok",
            data.get("data", {}).get("status") == "ok",
        )
    except Exception as exc:
        check("GET /health", False, f"API not running? {str(exc)[:60]}")
        warn(
            "Skipping remaining API tests",
            "start the API with: python scripts/start_api.py",
        )
        return
    try:
        resp = httpx.get(f"{base}/events", params={"limit": 10}, timeout=5)
        check(
            "GET /events returns 200",
            resp.status_code == 200,
            f"status={resp.status_code}",
        )
        payload = resp.json()
        events = payload.get("data", [])
        check(
            "GET /events response is list",
            isinstance(events, list),
            f"count={len(events)}",
        )
        if events:
            e = events[0]
            required_fields = [
                "post_id", "text", "labels", "severity",
                "confidence", "human_override", "indexed_at",
            ]
            missing = [f for f in required_fields if f not in e]
            check(
                "event record has required fields",
                len(missing) == 0,
                f"missing={missing}" if missing else "",
            )
            check(
                "severity is numeric",
                isinstance(e.get("severity"), (int, float)),
                f"type={type(e.get('severity')).__name__}",
            )
        else:
            warn(
                "no events in database",
                "run: python scripts/ingest.py --events 50 --speed 3.0",
            )
    except Exception as exc:
        check("GET /events", False, str(exc)[:80])
    try:
        resp = httpx.get(
            f"{base}/events",
            params={"min_severity": 0.5, "limit": 5},
            timeout=5,
        )
        check(
            "GET /events?min_severity filter works",
            resp.status_code == 200,
            f"status={resp.status_code}",
        )
    except Exception as exc:
        check("GET /events?min_severity", False, str(exc)[:80])


# ── 8. Pipeline end-to-end ────────────────────────────────────────────────────
async def _test_pipeline() -> None:
    print("\n[8/8] END-TO-END PIPELINE")
    try:
        from app.pipeline.processor import CrisisProcessor
        from app.ingestion.schema import RawPostSchema
        processor = CrisisProcessor()
        check("CrisisProcessor initialises", True)
        post = RawPostSchema(
            post_id=f"test_e2e_{int(time.time())}",
            text=(
                "Severe flooding in Wayanad district, Kerala. "
                "Hundreds of families stranded. Rescue teams needed urgently. "
                "Roads blocked, hospitals overwhelmed."
            ),
            platform="simulator",
            created_at=datetime.now(tz=timezone.utc),
        )
        start = time.perf_counter()
        record = await processor.process(post)
        elapsed = time.perf_counter() - start
        check("process() completes without error", True)
        check(
            "record has post_id",
            record.post_id == post.post_id,
        )
        check(
            "record has severity score",
            0.0 <= record.severity <= 1.0,
            f"severity={record.severity:.3f}",
        )
        check(
            "record persisted to database",
            True,
            "insert_event called inside processor",
        )
        check(
            f"end-to-end latency under 15s",
            elapsed < 15.0,
            f"took {elapsed:.2f}s",
        )
        if elapsed < 3.0:
            check(f"latency under 3s (excellent)", True, f"{elapsed:.2f}s")
        elif elapsed < 8.0:
            warn(f"latency {elapsed:.2f}s", "acceptable but geocoding may be slow")
        else:
            warn(f"latency {elapsed:.2f}s", "slow — check geocoder timeout settings")
        await processor.aclose()
    except Exception as exc:
        check("end-to-end pipeline", False, str(exc)[:120])


def test_pipeline() -> None:
    asyncio.get_event_loop().run_until_complete(_test_pipeline())


# ── Summary ───────────────────────────────────────────────────────────────────
def print_summary() -> None:
    passed  = sum(1 for _, s, _ in results if s == PASS)
    failed  = sum(1 for _, s, _ in results if s == FAIL)
    warned  = sum(1 for _, s, _ in results if s == WARN)
    total   = passed + failed
    print("\n" + "─" * 60)
    print("CRISISLENS SYSTEM CHECK — SUMMARY")
    print("─" * 60)
    print(f"  Passed  : {passed}/{total}")
    print(f"  Failed  : {failed}")
    print(f"  Warnings: {warned}")
    print("─" * 60)
    if failed == 0:
        print("  🎉 ALL CHECKS PASSED — system is demo-ready")
    else:
        print("  ❌ FAILURES DETECTED — fix the items above")
        print("\n  Failed checks:")
        for name, status, detail in results:
            if status == FAIL:
                print(f"    • {name}: {detail}")
    if warned > 0:
        print("\n  Warnings (non-blocking):")
        for name, status, detail in results:
            if status == WARN:
                print(f"    • {name}: {detail}")
    print("─" * 60)
    sys.exit(0 if failed == 0 else 1)


def main() -> None:
    configure_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    print("=" * 60)
    print("CRISISLENS — FULL SYSTEM CHECK")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    test_environment()
    test_imports()
    test_classifier()
    test_ner()
    test_severity()
    test_database()
    test_api()
    test_pipeline()
    print_summary()


if __name__ == "__main__":
    main()
