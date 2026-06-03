from __future__ import annotations

from app.core.config import settings

URGENCY_WEIGHTS: dict[str, float] = {
    "medical": 1.0,
    "earthquake": 0.9,
    "flood": 0.8,
    "fire": 0.75,
}


def compute_severity(label_probs: dict[str, float]) -> float:
    threshold: float = settings.CLASSIFIER_THRESHOLD
    scores: list[float] = [
        prob * URGENCY_WEIGHTS.get(label, 0.5)
        for label, prob in label_probs.items()
        if prob >= threshold and label in URGENCY_WEIGHTS
    ]
    return float(min(max(scores), 1.0)) if scores else 0.0
