from pathlib import Path

import openmeteo_requests
import pandas as pd
from retry_requests import retry
import requests_cache
import os
import logging

from app.utilities.utils import get_cloud_cover_emoji, get_timezone_from_coordinates


class OpenMeteoClient:
    _shared_session = None  # Class-level session
    _cache_expiry = 3600  # 1 hour

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.logger = logging.getLogger(__name__)
        self.timezone = get_timezone_from_coordinates(latitude, longitude)
        self.logger.info(f"Timezone for coordinates ({latitude}, {longitude}): {self.timezone}")

        # Initialize shared session once
        if OpenMeteoClient._shared_session is None:
            cache_dir = Path(os.getcwd()) / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)

            session = requests_cache.CachedSession(
                str(cache_dir / "meteo_cache"),
                expire_after=self._cache_expiry
            )
            retry_session = retry(session, retries=5, backoff_factor=0.2)
            OpenMeteoClient._shared_session = openmeteo_requests.Client(session=retry_session)

        self.client = OpenMeteoClient._shared_session
        self.logger.info("Using shared OpenMeteo session")

    def fetch_weather_data(self):
        """Instance method using shared client"""
        url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ["temperature_2m", "is_day", "precipitation", "cloud_cover"],
            "hourly": ["temperature_2m", "precipitation_probability", "precipitation", "cloud_cover", "visibility",
                       "is_day"],
            "daily": ["sunrise", "sunset", "precipitation_probability_max"],
            "timezone": self.timezone
        }

        try:
            self.response = self.client.weather_api(url, params=self.params)[0]
        except Exception as e:
            self.logger.error(f"Weather fetch failed: {e}")
            self.response = None

    def get_location_info(self) -> dict:
        """
        Get location information from the response attribute.

        :return: Dictionary with location information
        """
        if self.response is None:
            self.logger.error("No response data available. Please fetch the weather data first.")
            raise ValueError("No response data available. Please fetch the weather data first.")
        print(self.response)

        return {
            "latitude": self.response.Latitude(),
            "longitude": self.response.Longitude(),
            "timezone": [self.response.Timezone(), self.response.TimezoneAbbreviation()]
        }

    def get_current_weather(self) -> dict:
        """
        Get current weather information from the response attribute.

        :return: Dictionary with current weather information
        """
        if self.response is None:
            self.logger.error("No response data available. Please fetch the weather data first.")
            raise ValueError("No response data available. Please fetch the weather data first.")

        current = self.response.Current()
        return {
            "time": current.Time(),
            "temperature_2m": current.Variables(0).Value(),
            "is_day": current.Variables(1).Value(),
            "precipitation": current.Variables(2).Value(),
            "cloud_cover": current.Variables(3).Value(),
            "cloud_cover_emoji": get_cloud_cover_emoji(current.Variables(3).Value())
        }

    def get_hourly_weather(self) -> pd.DataFrame:
        """
        Get hourly weather information from the response attribute.

        :return: DataFrame with hourly weather information
        """
        if self.response is None:
            self.logger.error("No response data available. Please fetch the weather data first.")
            raise ValueError("No response data available. Please fetch the weather data first.")

        hourly = self.response.Hourly()
        hourly_data = {
            "date": pd.date_range(start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                                  end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                                  freq=pd.Timedelta(seconds=hourly.Interval()),
                                  inclusive="left"),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "precipitation_probability": hourly.Variables(1).ValuesAsNumpy(),
            "precipitation": hourly.Variables(2).ValuesAsNumpy(),
            "cloud_cover": hourly.Variables(3).ValuesAsNumpy(),
            "cloud_cover_emoji": [get_cloud_cover_emoji(cloud_cover) for cloud_cover in hourly.Variables(3).ValuesAsNumpy()],
            "visibility": hourly.Variables(4).ValuesAsNumpy(),
            "is_day": hourly.Variables(5).ValuesAsNumpy()
        }
        return pd.DataFrame(data=hourly_data)

    def get_daily_weather(self) -> dict:
        """
        Get daily weather information from the response attribute.

        :return: A dictionary with daily weather information, suitable for JSON serialization.
        """
        self.logger.info("Getting daily weather information")
        if self.response is None:
            self.logger.error("No response data available. Please fetch the weather data first.")
            raise ValueError("No response data available. Please fetch the weather data first.")

        daily = self.response.Daily()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ).strftime('%Y-%m-%dT%H:%M:%SZ').tolist(),  # Convert to string and then list
            "precipitation_probability_max": [float(i) for i in list(daily.Variables(2).ValuesAsNumpy())]  # Convert ndarray to list
        }

        return daily_data

