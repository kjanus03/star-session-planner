from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union

import requests
import requests_cache
import logging
import os


class ISSClient:
    """
    Client for fetching International Space Station (ISS) pass times using NASA's Open Notify API.
    """

    def __init__(self, latitude: float, longitude: float, cache_expiry: int = 3600):
        """
        Constructor for the ISSClient class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        :param cache_expiry: Cache expiry time in seconds (default: 3600)
        """
        self.logger = logging.getLogger(__name__)
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "http://api.open-notify.org/iss-pass.json"

        # Setup caching similar to other clients
        CACHE_DIR = Path(os.getcwd()) / "cache"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.session = requests_cache.CachedSession(
            str(CACHE_DIR / "iss_cache"),
            expire_after=cache_expiry
        )

        self.logger.info(f"Initialized ISSPassClient for coordinates ({latitude}, {longitude})")

    def get_passes(self, number_of_passes: int = 5) -> Union[List[Dict], None]:
        """
        Fetch ISS pass times for the location.
        :param number_of_passes: Number of passes to return (max 100)
        :return: List of pass events with UTC times and durations
        """
        try:
            self.logger.info("Fetching ISS pass times...")
            params = {
                "lat": self.latitude,
                "lon": self.longitude,
                "n": min(number_of_passes, 100)  # API limit protection
            }

            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("message") != "success":
                self.logger.error(f"API Error: {data.get('reason', 'Unknown error')}")
                return None

            processed_passes = []
            for pass_data in data["response"]:
                processed_passes.append({
                    "rise_time_utc": datetime.utcfromtimestamp(pass_data["risetime"]).isoformat(),
                    "duration_seconds": pass_data["duration"],
                    "latitude": self.latitude,
                    "longitude": self.longitude
                })

            self.logger.info(f"Successfully fetched {len(processed_passes)} ISS passes")
            return processed_passes

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching ISS pass data: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            self.logger.error(f"Data parsing error: {str(e)}")
            return None