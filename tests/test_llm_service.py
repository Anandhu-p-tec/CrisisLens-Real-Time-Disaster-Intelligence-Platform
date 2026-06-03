from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.reasoning.prompt_builder import build_reasoning_prompt
from app.classification.schema import ClassificationResultSchema, CrisisLabel
from app.extraction.schema import ExtractionResultSchema


@pytest.fixture
def classification() -> ClassificationResultSchema:
    return ClassificationResultSchema(
        post_id="p1",
        labels=[CrisisLabel.FLOOD],
        severity=0.82,
        confidence=0.91,
        raw_logits=[0.1, 0.9, 0.2, 0.1],
    )


@pytest.fixture
def extraction() -> ExtractionResultSchema:
    return ExtractionResultSchema(
        post_id="p1",
        locations=["Kerala"],
        coordinates=(10.8505, 76.2711),
        needs=["rescue", "water"],
        entities={"person": [], "org": []},
    )


def test_prompt_contains_label(
    classification: ClassificationResultSchema,
    extraction: ExtractionResultSchema,
) -> None:
    prompt = build_reasoning_prompt(classification, extraction, [])
    assert "flood" in prompt.lower()


def test_prompt_contains_severity(
    classification: ClassificationResultSchema,
    extraction: ExtractionResultSchema,
) -> None:
    prompt = build_reasoning_prompt(classification, extraction, [])
    assert "0.82" in prompt


def test_prompt_contains_coordinates(
    classification: ClassificationResultSchema,
    extraction: ExtractionResultSchema,
) -> None:
    prompt = build_reasoning_prompt(classification, extraction, [])
    assert "10.8505" in prompt


def test_prompt_includes_similar_texts(
    classification: ClassificationResultSchema,
    extraction: ExtractionResultSchema,
) -> None:
    similar = ["River burst in Thrissur", "Flood relief in Kochi"]
    prompt = build_reasoning_prompt(classification, extraction, similar)
    assert "Thrissur" in prompt
    assert "Kochi" in prompt


def test_prompt_instructs_json_response(
    classification: ClassificationResultSchema,
    extraction: ExtractionResultSchema,
) -> None:
    prompt = build_reasoning_prompt(classification, extraction, [])
    assert "JSON" in prompt or "json" in prompt.lower()
