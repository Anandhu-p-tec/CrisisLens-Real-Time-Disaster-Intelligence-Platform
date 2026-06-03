from __future__ import annotations

import pytest

from app.classification.schema import ClassificationResultSchema
from app.classification.schema import CrisisLabel
from app.classification.severity import compute_severity


def test_compute_severity_returns_zero_when_no_active_labels() -> None:
    result = compute_severity({})
    assert result == 0.0


def test_compute_severity_clamps_to_one() -> None:
    result = compute_severity({"medical": 1.0, "earthquake": 1.0, "flood": 1.0})
    assert result <= 1.0


def test_compute_severity_medical_higher_than_fire() -> None:
    medical = compute_severity({"medical": 0.9})
    fire = compute_severity({"fire": 0.9})
    assert medical > fire


def test_classification_result_schema_validates_severity_bounds() -> None:
    with pytest.raises(Exception):
        ClassificationResultSchema(
            post_id="x", labels=[], severity=1.5, confidence=0.5, raw_logits=[]
        )


def test_classification_result_schema_valid() -> None:
    schema = ClassificationResultSchema(
        post_id="test_001",
        labels=[CrisisLabel.FLOOD],
        severity=0.8,
        confidence=0.9,
        raw_logits=[0.1, 0.9, 0.2, 0.3],
    )
    assert schema.severity == 0.8
    assert CrisisLabel.FLOOD in schema.labels
