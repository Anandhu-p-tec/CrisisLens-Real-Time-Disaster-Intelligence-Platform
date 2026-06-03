from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    CLASSIFIER_MODEL_PATH: str = "models/crisis_classifier"
    CLASSIFIER_THRESHOLD: float = 0.45
    LLM_SEVERITY_THRESHOLD: float = 0.6
    GEOCODER_USER_AGENT: str = "crisislens-app"
    FAISS_INDEX_PATH: str = "data/faiss.index"
    DATABASE_URL: str = "data/crisislens.db"
    SIMULATOR_SPEED_FACTOR: float = 10.0
    LOG_LEVEL: str = "INFO"


settings = Settings()
