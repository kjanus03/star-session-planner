import json
import datetime
import logging
from typing import Any, Union

import pandas as pd


class JSONFormatter:
    """
    Class for formatting JSON response data into a human-readable format.
    """
    def __init__(self, data: dict[str, Any]):
        """
        Initialize the JSONFormatter with the JSON response data.
        :param data: JSON response data
        """
        self.logger = logging.getLogger(__name__)
        self.data = data

    def format(self) -> str:
        """
        Main method to format the entire JSON response.
        """
        formatted_text = []

        if 'terrain_types' in self.data:
            formatted_text.append(self._format_terrain_types(self.data['terrain_types']))

        if 'elevation' in self.data:
            formatted_text.append(self._format_elevation(self.data['elevation']))

        if 'location_info' in self.data:
            formatted_text.append(self._format_location_info(self.data['location_info']))

        if 'current_weather' in self.data:
            formatted_text.append(self._format_current_weather(self.data['current_weather']))

        if 'hourly_weather' in self.data:
            formatted_text.append(self.format_hourly_weather(self.data['hourly_weather']))

        if 'daily_weather' in self.data:
            formatted_text.append(self.format_daily_weather(self.data['daily_weather']))

        if 'urban_centers' in self.data:
            formatted_text.append(self._format_urban_centers(self.data['urban_centers']))

        if 'distance_from_urban_center' in self.data:
            formatted_text.append(self._format_distance_from_urban_center(self.data['distance_from_urban_center']))

        if 'nearest_urban_center' in self.data:
            formatted_text.append(self._format_nearest_urban_center(self.data['nearest_urban_center']))

        if 'astronomical_events' in self.data:
            formatted_text.append(self.format_astronomical_events(self.data['astronomical_events']))

        return '\n\n'.join(formatted_text)

    @staticmethod
    def _format_terrain_types(terrain_types: Union[str, list[str]]) -> str:
        """
        Format the terrain types into a human-readable string.
        :param terrain_types: Types of terrain
        :return: String representation of terrain types
        """
        return f"Terrain Types: {', '.join(terrain_types) if isinstance(terrain_types, list) else terrain_types}"

    @staticmethod
    def _format_elevation(elevation: float) -> str:
        """
        Format the elevation into a human-readable string.
        :param elevation: Elevation in meters
        :return: String representation of elevation
        """
        return f"Elevation: {elevation} meters"

    @staticmethod
    def _format_location_info(location_info: dict[str, Any]) -> str:
        """
        Format the location information into a human-readable string.
        :param location_info: Dictionary containing location information
        :return: String representation of location information
        """
        info = [f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in location_info.items()]
        return f"Location Information:\n" + "\n".join(info)

    @staticmethod
    def _format_current_weather(current_weather: dict[str, Any]) -> str:
        """
        Format the current weather into a human-readable string.
        :param current_weather: dictionary containing current weather information
        :return: String representation of current weather
        """
        weather = [f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in current_weather.items()]
        return f"Current Weather:\n" + "\n".join(weather)

    def format_hourly_weather(self, hourly_weather: list[dict[str, Any]]) -> str:
        """
        Format the hourly weather into a human-readable string.
        :param hourly_weather: list of dictionaries containing hourly weather information
        :return: String representation of hourly weather
        """
        hourly_weather_serializable = self.convert_to_serializable(hourly_weather)
        return "Hourly Weather:\n" + json.dumps(hourly_weather_serializable, indent=4)

    def format_daily_weather(self, daily_weather: list[dict[str, Any]]) -> str:
        """
        Format the daily weather into a human-readable string.
        :param daily_weather: List of dictionaries containing daily weather information
        :return: String representation of daily weather
        """
        daily_weather_serializable = self.convert_to_serializable(daily_weather)
        return "Daily Weather:\n" + json.dumps(daily_weather_serializable, indent=4)

    @staticmethod
    def _format_urban_centers(urban_centers: list[dict[str, Any]]) -> str:
        """
        Format the urban centers into a human-readable string.
        :param urban_centers: List of dictionaries containing urban center information
        :return: String representation of urban centers
        """
        centers = [f"{center['name']} ({center['latitude']}, {center['longitude']})" for center in urban_centers]
        return f"Urban Centers:\n" + "\n".join(centers)

    @staticmethod
    def _format_distance_from_urban_center(distance: float) -> str:
        """
        Format the distance from the nearest urban center into a human-readable string.
        :param distance: Distance in kilometers
        :return: String representation of distance from the nearest urban center
        """
        return f"Distance from Nearest Urban Center: {distance} km"

    @staticmethod
    def _format_nearest_urban_center(center: dict[str, Any]) -> str:
        """
        Format the nearest urban center into a human-readable string.
        :param center: Dictionary containing the name, latitude, and longitude of the nearest urban center
        :return: String representation of the nearest urban center
        """
        return f"Nearest Urban Center: {center['name']} ({center['latitude']}, {center['longitude']})"

    def format_astronomical_events(self, events: dict[str, Any]) -> str:
        """
        Format the astronomical events into a human-readable string.
        :param events: Dictionary containing astronomical events
        :return: String representation of astronomical events
        """
        event_strings = []
        for key, value in events.items():
            if isinstance(value, list):
                # Check if the list contains dictionaries
                if any(isinstance(item, dict) for item in value):
                    event_strings.append(
                        f"{key.replace('_', ' ').capitalize()}:\n" +
                        "\n".join([json.dumps(self.convert_to_serializable(item), indent=4) for item in value])
                    )
                else:
                    event_strings.append(f"{key.replace('_', ' ').capitalize()}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                event_strings.append(
                    f"{key.replace('_', ' ').capitalize()}:\n" + json.dumps(self.convert_to_serializable(value),
                                                                            indent=4)
                )
            else:
                event_strings.append(f"{key.replace('_', ' ').capitalize()}: {value}")
        return "Astronomical Events:\n" + "\n".join(event_strings)

    def convert_to_serializable(self, obj: Any) -> Any:
        """
        Convert non-serializable objects like Timestamp to a serializable format.
        """
        if isinstance(obj, dict):
            return {key: JSONFormatter.convert_to_serializable(self, value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [JSONFormatter.convert_to_serializable(self, item) for item in obj]
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, float):
            return str(round(obj, 5))
        else:
            self.logger.warning(f"Object of type {type(obj)} is not serializable.")
            return obj
