from __future__ import annotations

import pytest

from app.extraction.ner_pipeline import NERPipeline


@pytest.fixture(scope="module")
def ner() -> NERPipeline:
    return NERPipeline()


def test_ner_extracts_needs_keywords(ner: NERPipeline) -> None:
    result = ner.extract("p1", "People are trapped and need rescue in flooded area")
    assert "trapped" in result.needs
    assert "rescue" in result.needs


def test_ner_extracts_location(ner: NERPipeline) -> None:
    result = ner.extract("p2", "Flash flood hits Kerala, hundreds displaced")
    assert any("Kerala" in loc for loc in result.locations)


def test_ner_returns_correct_post_id(ner: NERPipeline) -> None:
    result = ner.extract("post_xyz", "Earthquake in Mumbai")
    assert result.post_id == "post_xyz"


def test_ner_coordinates_none_before_geocoding(ner: NERPipeline) -> None:
    result = ner.extract("p3", "Fire in Chennai market")
    assert result.coordinates is None


def test_ner_empty_text_does_not_crash(ner: NERPipeline) -> None:
    result = ner.extract("p4", "")
    assert result.locations == []
    assert result.needs == []
