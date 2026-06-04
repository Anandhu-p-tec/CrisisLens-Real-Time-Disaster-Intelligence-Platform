from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from datetime import timezone

from app.classification.classifier import CrisisClassifier
from app.core.config import settings
from app.core.logging import configure_logging
from app.extraction.geocoder import Geocoder
from app.extraction.ner_pipeline import NERPipeline
from app.ingestion.schema import RawPostSchema
from app.reasoning.llm_service import LLMService
from app.reasoning.rag_retriever import RAGRetriever
from app.repository.database import initialise_database
from app.repository.events import insert_event
from app.repository.schema import CrisisEventRecord

_logger = logging.getLogger(__name__)


class CrisisProcessor:
    def __init__(self) -> None:
        self._classifier = CrisisClassifier()
        self._ner = NERPipeline()
        self._geocoder = Geocoder()
        self._retriever = RAGRetriever()
        self._llm = LLMService(self._retriever)

    async def process(self, post: RawPostSchema) -> CrisisEventRecord:
        classification = await self._classifier.classify(post)
        extraction = self._ner.extract(post.post_id, post.text)
        if extraction.locations:
            extraction.coordinates = await self._geocoder.resolve(extraction.locations)

        reasoning = None
        recommended_action = None
        human_override = False

        _logger.info(
            "Classification complete: post=%s severity=%.2f threshold=%.2f",
            post.post_id,
            classification.severity,
            settings.LLM_SEVERITY_THRESHOLD,
        )

        if classification.severity >= settings.LLM_SEVERITY_THRESHOLD:
            try:
                llm_result = await self._llm.reason(post.text, classification, extraction)
                reasoning = llm_result.reasoning
                recommended_action = llm_result.recommended_action
                human_override = llm_result.human_override
                _logger.info("LLM reasoning enabled for post=%s", post.post_id)
            except Exception as exc:
                _logger.warning(
                    "LLM reasoning failed for post=%s: %s",
                    post.post_id,
                    exc,
                )

        record = CrisisEventRecord(
            post_id=post.post_id,
            text=post.text,
            platform=post.platform,
            created_at=post.created_at,
            labels=[str(l) for l in classification.labels],
            severity=classification.severity,
            confidence=classification.confidence,
            lat=extraction.coordinates[0] if extraction.coordinates else None,
            lng=extraction.coordinates[1] if extraction.coordinates else None,
            location_raw=extraction.locations[0] if extraction.locations else None,
            reasoning=reasoning,
            recommended_action=recommended_action,
            human_override=human_override,
            indexed_at=datetime.now(tz=timezone.utc),
        )
        await insert_event(record)
        _logger.info(
            "Processed post=%s labels=%s severity=%.2f",
            post.post_id,
            record.labels,
            record.severity,
        )
        return record

    async def aclose(self) -> None:
        if self._llm is not None:
            await self._llm.aclose()
