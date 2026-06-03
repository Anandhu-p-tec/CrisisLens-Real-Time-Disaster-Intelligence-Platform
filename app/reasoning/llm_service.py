from __future__ import annotations

import json
import logging

import httpx

from app.classification.schema import ClassificationResultSchema
from app.core.config import settings
from app.core.exceptions import ReasoningError
from app.extraction.schema import ExtractionResultSchema
from app.reasoning.prompt_builder import build_reasoning_prompt
from app.reasoning.rag_retriever import RAGRetriever
from app.reasoning.schema import ReasoningResultSchema

_logger = logging.getLogger(__name__)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


class LLMService:
    def __init__(self, retriever: RAGRetriever) -> None:
        self._retriever = retriever
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=5.0,
        )
        _logger.info("LLMService initialised with model=%s timeout=5.0s", GROQ_MODEL)

    async def reason(
        self,
        post_text: str,
        classification: ClassificationResultSchema,
        extraction: ExtractionResultSchema,
    ) -> ReasoningResultSchema:
        similar_texts = self._retriever.retrieve(text=post_text, k=3)
        prompt = build_reasoning_prompt(classification, extraction, similar_texts)
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a crisis intelligence analyst. "
                        "Respond only with valid JSON matching the schema given. "
                        "No preamble. No markdown. No explanation outside the JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        }
        _logger.debug("Calling Groq API for post=%s", classification.post_id)
        try:
            response = await self._client.post(GROQ_API_URL, json=payload)
            response.raise_for_status()
            _logger.debug("Groq API returned status=%s", response.status_code)
        except httpx.TimeoutException as exc:
            _logger.error("Groq API timeout after 5s")
            raise ReasoningError("Groq API timeout") from exc
        except httpx.HTTPStatusError as exc:
            _logger.error("Groq API error: %s", exc.response.status_code)
            raise ReasoningError(f"Groq API error: {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            _logger.error("Groq request failed: %s", exc)
            raise ReasoningError(f"Groq request failed: {exc}") from exc

        raw_text = response.json()["choices"][0]["message"]["content"].strip()
        _logger.debug("LLM raw response: %s", raw_text[:100])
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            _logger.error("LLM returned invalid JSON: %s", raw_text[:200])
            raise ReasoningError(f"LLM returned invalid JSON: {raw_text[:200]}") from exc

        confidence_level = parsed.get("confidence_level", "low")
        if confidence_level not in ("high", "medium", "low"):
            confidence_level = "low"

        _logger.info("LLM reasoning complete: post=%s confidence=%s", classification.post_id, confidence_level)
        return ReasoningResultSchema(
            post_id=classification.post_id,
            reasoning=parsed.get("reasoning", ""),
            recommended_action=parsed.get("recommended_action", ""),
            confidence_level=confidence_level,
            human_override=confidence_level == "low",
            similar_event_ids=[],
        )

    async def aclose(self) -> None:
        await self._client.aclose()
