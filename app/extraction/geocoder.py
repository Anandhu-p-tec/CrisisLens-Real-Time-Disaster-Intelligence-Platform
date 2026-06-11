from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from geopy.exc import GeocoderServiceError
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from app.core.config import settings
from app.core.exceptions import ExtractionError

_logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2)


class Geocoder:
    def __init__(self) -> None:
        self._geolocator = Nominatim(user_agent=settings.GEOCODER_USER_AGENT)
        _logger.info(
            "Geocoder initialised with user_agent=%s", settings.GEOCODER_USER_AGENT
        )

    def _geocode_sync(self, location: str) -> tuple[float, float] | None:
        try:
            # Clean location: remove surrounding brackets/quotes and whitespace
            cleaned = location.strip().strip("[]()\"' ")
            # Skip overly vague single-token locations that won't geocode well
            VAGUE_TOKENS = {
                "india",
                "city",
                "district",
                "area",
                "region",
                "village",
                "state",
                "north",
                "south",
                "east",
                "west",
                "central",
                "nearby",
                "here",
                "there",
                "near",
                "town",
                "suburb",
                "market",
            }
            tokens = cleaned.split()
            if len(tokens) == 1 and tokens[0].lower() in VAGUE_TOKENS:
                _logger.debug("Skipping vague location token: %s", cleaned)
                return None
            # Bias search to India for better local results
            query = f"{cleaned}, India"
            time.sleep(1.1)  # Nominatim ToS: max 1 request per second
            result = self._geolocator.geocode(query, timeout=10)
            if result is not None:
                return (result.latitude, result.longitude)
            return None
        except (GeocoderServiceError, GeocoderTimedOut):
            _logger.debug("Geocoding failed for: %s", location)
            return None

    async def resolve(self, locations: list[str]) -> tuple[float, float] | None:
        loop = asyncio.get_event_loop()
        for location in locations:
            coords = await loop.run_in_executor(_executor, self._geocode_sync, location)
            if coords is not None:
                return coords
        return None
