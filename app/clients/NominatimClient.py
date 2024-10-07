import logging
import requests

class NominatimClient:
    """
    Client for fetching latitude and longitude from a city name using the Nominatim API.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.city_name = ""
        self.base_url = ""


    def get_lat_lon(self, city_name: str) -> dict[str, float]:
        """
        Get latitude and longitude for a given city name.
        :param city_name:
        :return:
        """
        self.logger.info(f"Fetching latitude and longitude for city: {city_name}")
        self.base_url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json&limit=1"
        self.city_name = city_name
        response = requests.get(self.base_url)

        if response.status_code == 200 and len(response.json()) > 0:
            self.logger.info(f"Latitude and longitude fetched successfully for city: {city_name}")
            data = response.json()[0]
            return {
                'latitude': float(data['lat']),
                'longitude': float(data['lon'])
            }
        else:
            self.logger.error(f"Error fetching latitude and longitude for city: {city_name}")

