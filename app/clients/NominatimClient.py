import logging
from functools import lru_cache

import requests

class NominatimClient:
    """
    Client for fetching latitude and longitude from a city name using the Nominatim API.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.city_name = ""
        self.base_url = ""


    # not instance based method for proper caching
    @classmethod
    @lru_cache(maxsize=128)
    def get_lat_lon(cls, city_name: str) -> dict[str, float]:
        """
        Get latitude and longitude for a given city name.
        :param city_name:
        :return:
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Fetching coordinates for {city_name}")
        url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json&limit=1"
        response = requests.get(url)

        if response.status_code == 200 and len(response.json()) > 0:
            logger.info(f"Latitude and longitude fetched successfully for city: {city_name}")
            data = response.json()[0]
            return {
                'latitude': float(data['lat']),
                'longitude': float(data['lon'])
            }
        else:
            logger.error(f"Error fetching latitude and longitude for city: {city_name}")

