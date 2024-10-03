import json
import datetime
import logging
from typing import Any, Union

import numpy as np
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
            formatted_text.append(self.format_terrain_types(self.data['terrain_types']))

        if 'elevation' in self.data:
            formatted_text.append(self.format_elevation(self.data['elevation']))

        if 'location_info' in self.data:
            formatted_text.append(self.format_location_info(self.data['location_info']))

        if 'current_weather' in self.data:
            formatted_text.append(self.format_current_weather(self.data['current_weather']))

        if 'hourly_weather' in self.data:
            formatted_text.append(self.format_hourly_weather(self.data['hourly_weather']))

        if 'daily_weather' in self.data:
            formatted_text.append(self.format_daily_weather(self.data['daily_weather']))

        if 'urban_centers' in self.data:
            formatted_text.append(self.format_urban_centers(self.data['urban_centers']))

        if 'distance_from_urban_center' in self.data:
            formatted_text.append(self.format_distance_from_urban_center(self.data['distance_from_urban_center']))

        if 'nearest_urban_center' in self.data:
            formatted_text.append(self.format_nearest_urban_center(self.data['nearest_urban_center']))

        if 'astronomical_events' in self.data:
            formatted_text.append(self.format_astronomical_events(self.data['astronomical_events']))

        return '\n\n'.join(formatted_text)

    def format_terrain_types(self, terrain_types: Union[str, list[str]]) -> str:
        """
        Format the terrain types into a human-readable string.
        """
        self.logger.info(f"Formatting terrain types")
        return f"Terrain Types: {', '.join(map(str, self.convert_to_serializable(terrain_types)))}"

    def format_elevation(self, elevation: float) -> str:
        """
        Format the elevation into a human-readable string.
        """
        self.logger.info(f"Formatting elevation")
        elevation_serializable = self.convert_to_serializable(elevation)
        return f"Elevation: {elevation_serializable} meters"

    def format_location_info(self, location_info: dict[str, Any]) -> str:
        """
        Format the location information into a human-readable string.
        """
        self.logger.info(f"Formatting location information")
        info = [
            f"{key.replace('_', ' ').capitalize()}: {self.convert_to_serializable(value)}"
            for key, value in location_info.items()
        ]
        return f"Location Information:\n" + "\n".join(info)


    def format_current_weather(self, current_weather: dict[str, Any]) -> str:
        """
        Format the current weather into a human-readable string.
        """
        self.logger.info(f"Formatting current weather")
        cloud_cover = self.convert_to_serializable(current_weather['cloud_cover'])

        weather = [
            f"Cloud Cover: {cloud_cover}",
            f"Time of Day: {'Day' if current_weather['is_day'] else 'Night'}",
            f"Precipitation: {self.convert_to_serializable(current_weather['precipitation'])} mm",
            f"Temperature: {self.convert_to_serializable(current_weather['temperature_2m']):.2f} °C",
            f"Time: {datetime.datetime.fromtimestamp(self.convert_to_serializable(current_weather['time'])).strftime('%d.%m.%Y, %H:%M:%S')}"
        ]
        print(weather)
        return f"Current Weather:\n" + "\n".join(weather)

    def format_hourly_weather(self, hourly_weather: list[dict[str, Any]]) -> str:
        """
        Format the hourly weather into a human-readable string.
        """
        self.logger.info(f"Formatting hourly weather")
        weather_entries = []
        for hour in hourly_weather:
            cloud_cover = self.convert_to_serializable(hour['cloud_cover'])

            entry = (
                f"{datetime.datetime.fromisoformat(str(hour['date'])).strftime('%d.%m.%Y, %H:%M:%S')}: "
                f"{self.convert_to_serializable(hour['temperature_2m']):.2f}°C, "
                f"Precipitation: {self.convert_to_serializable(hour['precipitation'])}mm, "
                f"Cloud Cover: {cloud_cover}"
            )
            weather_entries.append(entry)
        print(weather_entries)
        return "Hourly Weather:\n" + "\n".join(weather_entries)

    def format_daily_weather(self, daily_weather: list[dict[str, Any]]) -> str:
        """
        Format the daily weather into a human-readable string.
        """
        self.logger.info(f"Formatting daily weather")
        daily_weather_serializable = self.convert_to_serializable(daily_weather)
        return "Daily Weather:\n" + json.dumps(daily_weather_serializable, indent=4)


    def format_urban_centers(self, urban_centers: list[dict[str, Any]]) -> str:
        """
        Format the urban centers into a human-readable string.
        """
        self.logger.info(f"Formatting urban centers")
        centers = [
            f"{center['name']} ({self.convert_to_serializable(center['latitude'])}, {self.convert_to_serializable(center['longitude'])})"
            for center in urban_centers
        ]
        return f"Urban Centers:\n" + "\n".join(centers)


    def format_distance_from_urban_center(self, distance: float) -> str:
        """
        Format the distance from the nearest urban center into a human-readable string.
        """
        self.logger.info(f"Formatting distance from urban center")
        distance_serializable = self.convert_to_serializable(distance)
        return f"Distance from Nearest Urban Center: {distance_serializable} km"

    def format_nearest_urban_center(self, center: dict[str, Any]) -> str:
        """
        Format the nearest urban center into a human-readable string.
        """
        self.logger.info(f"Formatting nearest urban center")
        latitude = self.convert_to_serializable(center['latitude'])
        longitude = self.convert_to_serializable(center['longitude'])
        return f"Nearest Urban Center: {center['name']} ({latitude}, {longitude})"

    def format_astronomical_events(self, events: dict[str, Any]) -> str:
        """
        Format the astronomical events into a human-readable string.
        """
        self.logger.info(f"Formatting astronomical events")
        event_strings = []
        for key, value in events.items():
            if isinstance(value, list):
                # Convert all items in the list to serializable format
                serializable_items = [self.convert_to_serializable(item) for item in value]

                if any(isinstance(item, dict) for item in serializable_items):
                    # If the list contains dictionaries, format them nicely
                    event_strings.append(
                        f"{key.replace('_', ' ').capitalize()}:\n" +
                        "\n".join([json.dumps(item, indent=4) for item in serializable_items])
                    )
                else:
                    # If the list contains simple values, just join them into a string
                    event_strings.append(
                        f"{key.replace('_', ' ').capitalize()}: {', '.join(map(str, serializable_items))}")
            elif isinstance(value, dict):
                # If the value is a dictionary, convert it and serialize it
                serializable_value = self.convert_to_serializable(value)
                event_strings.append(
                    f"{key.replace('_', ' ').capitalize()}:\n" + json.dumps(serializable_value, indent=4)
                )
            else:
                # For simple values, convert to serializable and then append
                serializable_value = self.convert_to_serializable(value)
                event_strings.append(f"{key.replace('_', ' ').capitalize()}: {serializable_value}")

        return "Astronomical Events:\n" + "\n".join(event_strings)

    def convert_to_serializable(self, obj: Any) -> Any:
        """
        Convert non-serializable objects like bytes or Timestamp to a serializable format.
        """
        # self.logger.info(f"Converting object to serializable")
        try:
            if isinstance(obj, dict):
                return {key: self.convert_to_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [self.convert_to_serializable(item) for item in obj]
            elif isinstance(obj, np.generic):
                return obj.item()  # Convert numpy types to native Python types
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            elif isinstance(obj, bytes):
                return obj.decode('utf-8')  # Properly decode bytes to string
            elif isinstance(obj, (int, str, float, bool, type(None))):
                return obj  # Keep serializable types as they are
            else:
                self.logger.warning(f"Object of type {type(obj)} is not serializable and will be omitted.")
                return None  # Omit non-serializable values
        except Exception as e:
            self.logger.error(f"Error converting object to serializable: {e}")
            return None