from pathlib import Path
from typing import Union

import requests_cache
import logging
import os


class OpenElevationClient:
    """
    Client for fetching elevation data from the Open-Elevation API.
    """
    _session = None  # Class-level shared session
    _cache_expiry = 3600  # 1 hour

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.logger = logging.getLogger(__name__)

        # Initialize class-level session once
        if OpenElevationClient._session is None:
            cache_dir = Path(os.getcwd()) / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)

            OpenElevationClient._session = requests_cache.CachedSession(str(cache_dir / "elevation.db"),
                expire_after=self._cache_expiry)
            self.logger.info("Initialized shared elevation cache session")

    def fetch_elevation(self) -> Union[float, None]:
        """Instance method using shared session"""
        url = "https://api.open-elevation.com/api/v1/lookup"
        payload = {"locations": [{"latitude": self.latitude, "longitude": self.longitude}]}

        try:
            response = self._session.post(url, json=payload)
            response.raise_for_status()
            return response.json()['results'][0]['elevation']
        except Exception as e:
            self.logger.error(f"Elevation fetch failed: {e}")
            return None
