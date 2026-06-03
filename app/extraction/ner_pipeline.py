from __future__ import annotations

import logging

import spacy

from app.core.exceptions import ExtractionError
from app.extraction.schema import ExtractionResultSchema

_logger = logging.getLogger(__name__)

NEED_KEYWORDS: frozenset[str] = frozenset(
    {
        "rescue",
        "trapped",
        "food",
        "water",
        "medical",
        "help",
        "shelter",
        "injured",
        "stranded",
        "evacuation",
        "missing",
        "dead",
        "urgent",
        "emergency",
        "fire",
        "flood",
        "collapsed",
        "blocked",
        "danger",
    }
)


class NERPipeline:
    def __init__(self) -> None:
        self._nlp = spacy.load("en_core_web_sm")
        _logger.info("NERPipeline loaded")

    def extract(self, post_id: str, text: str) -> ExtractionResultSchema:
        try:
            doc = self._nlp(text)
        except Exception as exc:
            raise ExtractionError(f"spaCy failed on post {post_id}") from exc
        locations: list[str] = [
            ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "FAC")
        ]
        persons: list[str] = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        orgs: list[str] = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        lowered = text.lower()
        needs: list[str] = [kw for kw in NEED_KEYWORDS if kw in lowered]
        return ExtractionResultSchema(
            post_id=post_id,
            locations=locations,
            coordinates=None,
            needs=needs,
            entities={"person": persons, "org": orgs},
        )
