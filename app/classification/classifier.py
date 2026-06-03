from __future__ import annotations

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer

from app.classification.schema import ClassificationResultSchema
from app.classification.schema import CrisisLabel
from app.classification.severity import compute_severity
from app.core.config import settings
from app.ingestion.schema import RawPostSchema

_logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=1)


class CrisisClassifier:
    def __init__(self) -> None:
        model_path = str(settings.CLASSIFIER_MODEL_PATH)
        self._tokenizer = AutoTokenizer.from_pretrained(model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self._model.eval()
        label_map_path = Path("data/processed/label_map.json")
        with label_map_path.open() as f:
            data = json.load(f)
        self._id2label: dict[int, str] = {int(k): v for k, v in data["id2label"].items()}
        _logger.info("CrisisClassifier loaded from %s", model_path)

    def _sigmoid(self, logits: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-logits))

    def _infer(self, post: RawPostSchema) -> ClassificationResultSchema:
        inputs = self._tokenizer(
            post.text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding="max_length",
        )
        inputs.pop("token_type_ids", None)
        with torch.no_grad():
            output = self._model(**inputs)
        logits: np.ndarray = output.logits.numpy()[0]
        probs: np.ndarray = self._sigmoid(logits)
        label_probs: dict[str, float] = {
            self._id2label[i]: float(probs[i]) for i in range(len(probs))
        }
        active_labels: list[CrisisLabel] = [
            CrisisLabel(label)
            for label, prob in label_probs.items()
            if prob >= settings.CLASSIFIER_THRESHOLD
        ]
        severity: float = compute_severity(label_probs)
        confidence: float = float(max(probs))
        return ClassificationResultSchema(
            post_id=post.post_id,
            labels=active_labels,
            severity=severity,
            confidence=confidence,
            raw_logits=logits.tolist(),
        )

    async def classify(self, post: RawPostSchema) -> ClassificationResultSchema:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._infer, post)
