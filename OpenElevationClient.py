import requests


class OpenElevationClient:
    """
    Client for fetching elevation data from the Open-Elevation API.
    """
    def __init__(self, latitude: float, longitude: float):
        """
        Constructor for the OpenElevationClient class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        """
        self.latitude = latitude
        self.longitude = longitude
        self.elevation_url = "https://api.open-elevation.com/api/v1/lookup"

    def fetch_elevation(self) -> float:
        """
        Fetch elevation data from the Open-Elevation API.
        :return: Elevation in meters
        """
        payload = {"locations": [{"latitude": self.latitude, "longitude": self.longitude}]}
        response = requests.post(self.elevation_url, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        elevation = data['results'][0]['elevation']
        return elevation

