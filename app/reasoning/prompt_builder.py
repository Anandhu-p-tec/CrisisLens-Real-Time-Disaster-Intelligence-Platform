from __future__ import annotations

from app.classification.schema import ClassificationResultSchema
from app.extraction.schema import ExtractionResultSchema


def build_reasoning_prompt(
    classification: ClassificationResultSchema,
    extraction: ExtractionResultSchema,
    similar_texts: list[str],
) -> str:
    labels_str = ", ".join(classification.labels) if classification.labels else "unknown"
    coords_str = (
        f"{extraction.coordinates[0]:.4f}, {extraction.coordinates[1]:.4f}"
        if extraction.coordinates
        else "unresolved"
    )
    similar_block = "\n".join(
        f"{i + 1}. \"{text}\"" for i, text in enumerate(similar_texts[:3])
    )
    return (
        f"New crisis post classified as: {labels_str}\n"
        f"Severity score: {classification.severity:.2f}\n"
        f"Location resolved: {coords_str}\n"
        f"Needs detected: {', '.join(extraction.needs) or 'none'}\n\n"
        f"Similar past events:\n{similar_block}\n\n"
        f"In exactly 2 sentences, explain why this is a {labels_str} event at severity "
        f"{classification.severity:.2f}. Then state the single most important first action "
        f"for an emergency response team. Respond only in this JSON format:\n"
        f'{{"reasoning": "...", "recommended_action": "...", "confidence_level": "high|medium|low"}}'
    )
