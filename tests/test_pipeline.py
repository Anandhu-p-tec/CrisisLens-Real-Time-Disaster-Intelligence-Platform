from __future__ import annotations

import asyncio
from datetime import datetime
from datetime import timezone
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.ingestion.schema import RawPostSchema


@pytest.fixture
def sample_post() -> RawPostSchema:
    return RawPostSchema(
        post_id="test_001",
        text="Flooding in Wayanad, people trapped on rooftops need rescue",
        platform="simulator",
        created_at=datetime.now(tz=timezone.utc),
    )


@pytest.mark.asyncio
async def test_processor_returns_record_with_correct_post_id(
    sample_post: RawPostSchema,
) -> None:
    with (
        patch("app.pipeline.processor.CrisisClassifier") as MockClassifier,
        patch("app.pipeline.processor.NERPipeline") as MockNER,
        patch("app.pipeline.processor.Geocoder") as MockGeocoder,
        patch("app.pipeline.processor.RAGRetriever") as MockRetriever,
        patch("app.pipeline.processor.LLMService") as MockLLM,
        patch("app.pipeline.processor.insert_event", new_callable=AsyncMock),
    ):
        from app.classification.schema import ClassificationResultSchema
        from app.classification.schema import CrisisLabel
        from app.extraction.schema import ExtractionResultSchema

        mock_classification = ClassificationResultSchema(
            post_id="test_001",
            labels=[CrisisLabel.FLOOD],
            severity=0.75,
            confidence=0.88,
            raw_logits=[0.1, 0.9, 0.2, 0.3],
        )
        mock_extraction = ExtractionResultSchema(
            post_id="test_001",
            locations=["Wayanad"],
            coordinates=(11.6854, 76.1320),
            needs=["rescue", "trapped"],
            entities={"person": [], "org": []},
        )

        MockClassifier.return_value.classify = AsyncMock(
            return_value=mock_classification
        )
        MockNER.return_value.extract = MagicMock(return_value=mock_extraction)
        MockGeocoder.return_value.resolve = AsyncMock(
            return_value=(11.6854, 76.1320)
        )
        MockRetriever.return_value = MagicMock()
        MockLLM.return_value = MagicMock()

        from app.pipeline.processor import CrisisProcessor

        processor = CrisisProcessor()
        record = await processor.process(sample_post)
        assert record.post_id == "test_001"
        assert record.severity == 0.75
        assert "flood" in record.labels
