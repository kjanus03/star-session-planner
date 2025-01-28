from functools import lru_cache
from pytz import timezone
from skyfield.api import load, Topos
from skyfield.almanac import find_discrete, risings_and_settings, moon_phases, MOON_PHASES
from datetime import datetime
from typing import Any
import logging
import os
import json
from app.utilities.utils import get_timezone_from_coordinates


class AstronomicalEvents:
    """
    Class for finding astronomical events like visible planets, conjunctions, meteor showers, and moon info.
    """

    def __init__(self, latitude: float, longitude: float):
        """
        Constructor for the AstronomicalEvents class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        """
        self.logger = logging.getLogger(__name__)
        self.ts = load.timescale()
        self.logger.info("Loading ephemeris data...")
        self.eph = load('app/static/data/de430.bsp')
        self.logger.info("Ephemeris data loaded successfully.")
        self.location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        self.meteor_shower_data = self.load_meteor_shower_data()

    def get_alt_az(self, planet_barycenter: str, time) -> tuple[float, float]:
        """
        Helper function to compute the altitude and azimuth for a given planet at a specific time.
        :param planet_barycenter: Barycenter name of the planet
        :param time: Time for which to compute the coordinates
        :return: A tuple containing altitude and azimuth in degrees
        """
        planet = self.eph[planet_barycenter]
        astrometric = (self.eph['earth'] + self.location).at(time).observe(planet)
        alt, az, _ = astrometric.apparent().altaz()
        return float(alt.degrees), float(az.degrees)

    @lru_cache(maxsize=128)
    def visible_planets(self, date: datetime) -> list[dict[str, Any]]:
        """
        Find planets visible at night for a given date using barycenters, and include their sky coordinates.
        The function filters planets that are visible between sunset and sunrise.

        :param date: Datetime object representing the date.
        :return: A list of dictionaries containing the name of the planet, the time it rises, the time it sets, and its sky coordinates.
        """
        self.logger.info("Calculating visible planets...")

        t0 = self.ts.utc(date.year, date.month, date.day, 0, 0, 0)  # Start of day
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)  # End of day

        sunrise_time, sunset_time = self.get_sunrise_sunset(date)
        visible_planets = []

        for planet_name, planet_barycenter in [('Mars', 'mars barycenter'), ('Venus', 'venus barycenter'),
                                               ('Jupiter', 'jupiter barycenter'), ('Saturn', 'saturn barycenter'),
                                               ('Mercury', 'mercury barycenter')]:

            try:
                planet = self.eph[planet_barycenter]
                f_planet = risings_and_settings(self.eph, planet, self.location)
                planet_times, planet_is_rise = find_discrete(t0, t1, f_planet)

                rise_time, set_time, rise_altitude, rise_azimuth, set_altitude, set_azimuth = None, None, None, None, None, None

                for time, rise in zip(planet_times, planet_is_rise):
                    if rise:
                        rise_time = time.utc_iso()
                        rise_altitude, rise_azimuth = self.get_alt_az(planet_barycenter, time)
                    else:
                        set_time = time.utc_iso()
                        set_altitude, set_azimuth = self.get_alt_az(planet_barycenter, time)

                    if rise_time and set_time:
                        local_tz = sunrise_time.tzinfo
                        rise_time_aware = datetime.strptime(rise_time[:-1], "%Y-%m-%dT%H:%M:%S").replace(
                            tzinfo=timezone('UTC')).astimezone(local_tz)
                        # set_time_aware = datetime.strptime(set_time[:-1], "%Y-%m-%dT%H:%M:%S").replace(
                        #     tzinfo=timezone('UTC')).astimezone(local_tz)

                        if rise_time_aware < sunrise_time or rise_time_aware > sunset_time:
                            visible_planets.append({
                                'planet': planet_name,
                                'rise_time': rise_time,
                                'set_time': set_time,
                                'rise_altitude': rise_altitude,
                                'rise_azimuth': rise_azimuth,
                                'set_altitude': set_altitude,
                                'set_azimuth': set_azimuth
                            })
                        rise_time = None
                        set_time = None

            except Exception as e:
                self.logger.error(f"Error observing planet {planet_name}: {e}")
                continue  # Continue to the next planet

        if not visible_planets:
            self.logger.info(f"No planets visible for {date} between sunset and sunrise.")

        self.logger.info("Visible planets calculation completed.")
        return visible_planets

    @lru_cache(maxsize=128)
    def get_risings_and_settings(self, date: datetime, body: str) -> tuple:
        """
        Helper method to calculate the rising and setting times for a given celestial body.
        :param date: Datetime object representing the date.
        :param body: Name of the celestial body (e.g., 'sun', 'moon').
        :return: Tuple containing the times of rise/set and boolean flags indicating if it's a rise.
        """
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)
        f = risings_and_settings(self.eph, self.eph[body], self.location)
        times, is_rise = find_discrete(t0, t1, f)
        return times, is_rise

    @lru_cache(maxsize=128)
    def check_conjunctions(self, date: datetime) -> list[tuple[str, str]]:
        """
        Check for planetary conjunctions at a given date using barycenters.
        :param date: Datetime object representing date for which to check conjunctions
        :return: List of tuples containing the names of the planets in conjunction and the time of the event
        """
        self.logger.info("Checking for planetary conjunctions...")
        times, is_rise = self.get_risings_and_settings(date, 'sun')
        conjunctions = []
        for time, rise in zip(times, is_rise):
            if not rise:
                continue
            for planet1_name, planet1_barycenter in [('Mars', 'mars barycenter'), ('Venus', 'venus barycenter'),
                                                     ('Jupiter', 'jupiter barycenter'), ('Saturn', 'saturn barycenter'),
                                                     ('Mercury', 'mercury barycenter')]:
                for planet2_name, planet2_barycenter in [('Mars', 'mars barycenter'), ('Venus', 'venus barycenter'),
                                                         ('Jupiter', 'jupiter barycenter'),
                                                         ('Saturn', 'saturn barycenter'),
                                                         ('Mercury', 'mercury barycenter')]:
                    if planet1_name == planet2_name:
                        continue
                    planet1 = self.eph[planet1_barycenter]
                    planet2 = self.eph[planet2_barycenter]
                    astrometric1 = (self.eph['earth'] + self.location).at(time).observe(planet1)
                    astrometric2 = (self.eph['earth'] + self.location).at(time).observe(planet2)
                    alt1, az1, _ = astrometric1.apparent().altaz()
                    alt2, az2, _ = astrometric2.apparent().altaz()
                    if abs(alt1.degrees - alt2.degrees) < 1 and abs(az1.degrees - az2.degrees) < 1:
                        conjunctions.append((f"{planet1_name}-{planet2_name}", time.utc_iso()))
        self.logger.info("Planetary conjunctions checked successfully.")
        return conjunctions

    @lru_cache(maxsize=128)
    def load_meteor_shower_data(self) -> list[dict[str, Any]]:
        """
        Load meteor shower data from a JSON file.
        :return: Dictionary containing meteor shower data
        """
        self.logger.info("Loading meteor shower data...")
        file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'data', 'meteor_showers.json')
        with open(file_path, 'r') as file:
            return json.load(file)

    @lru_cache(maxsize=128)
    def check_meteor_showers(self, date: datetime) -> list[dict[str, Any]]:
        """
        Check for meteor showers at a given date.
        :param date: Datetime object representing date for which to check meteor showers
        :return: List of meteor showers active on the given date
        """
        self.logger.info("Checking for meteor showers...")

        showers = []
        for shower in self.meteor_shower_data:
            start_date = datetime.strptime(shower['start'], "%Y-%m-%d")
            end_date = datetime.strptime(shower['end'], "%Y-%m-%d")
            if start_date <= date <= end_date:
                showers.append(shower)
        return showers

    @lru_cache(maxsize=128)
    def moon_info(self, date: datetime) -> dict[str, Any]:
        """
        Get moonrise, moonset, and moon phase information for a given date.
        :param date: Datetime object representing the date for which to get moon information
        :return: Dictionary containing moonrise, moonset times, and moon phase
        """
        self.logger.info("Getting moon information...")
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)

        f = risings_and_settings(self.eph, self.eph['moon'], self.location)
        moonrise_set_times, is_moonrise = find_discrete(t0, t1, f)

        moonrise = None
        moonset = None
        for time, rise in zip(moonrise_set_times, is_moonrise):
            if rise:
                moonrise = time.utc_iso()
            else:
                moonset = time.utc_iso()

        moon_phase = MOON_PHASES[moon_phases(self.eph)(t0)]

        self.logger.info("Moon information retrieved successfully.")
        return {'moonrise': moonrise, 'moonset': moonset, 'moon_phase': moon_phase}

    @lru_cache(maxsize=128)
    def get_sunrise_sunset(self, date: datetime) -> tuple[datetime, datetime]:
        """
        Get sunrise and sunset times for a given date and convert them to the local time based on the location's timezone.

        :return: A tuple containing the local sunrise and sunset times.
        """
        self.logger.info("Getting sunrise and sunset times in UTC...")

        times, is_rise = self.get_risings_and_settings(date, 'sun')
        sunrise_utc = None
        sunset_utc = None
        for time, rise in zip(times, is_rise):
            if rise:
                sunrise_utc = datetime.strptime(time.utc_iso()[:-1], "%Y-%m-%dT%H:%M:%S")
            else:
                sunset_utc = datetime.strptime(time.utc_iso()[:-1], "%Y-%m-%dT%H:%M:%S")

        if not sunrise_utc or not sunset_utc:
            self.logger.error("Failed to retrieve sunrise or sunset times.")
            return sunrise_utc, sunset_utc

        latitude, longitude = self.location.latitude.degrees, self.location.longitude.degrees
        local_tz = get_timezone_from_coordinates(latitude, longitude)

        if not local_tz:
            self.logger.error(f"Timezone could not be found for coordinates {latitude}, {longitude}.")
            return sunrise_utc, sunset_utc

        sunrise_local = sunrise_utc.replace(tzinfo=timezone('UTC')).astimezone(local_tz)
        sunset_local = sunset_utc.replace(tzinfo=timezone('UTC')).astimezone(local_tz)
        self.logger.info(f"Sunrise: {sunrise_local}, Sunset: {sunset_local} in local time.")

        return sunrise_local, sunset_local

    @lru_cache(128)
    def get_sun_info(self, date: datetime) -> dict[str, str]:
        sunrise, sunset = self.get_sunrise_sunset(date)
        format_time = lambda t: f"{t.hour:02}:{t.minute:02}"

        return {'sunrise': format_time(sunrise), 'sunset': format_time(sunset)}

    @lru_cache(maxsize=128)
    def get_astronomical_events(self, date: datetime) -> dict[str, Any]:
        """
        Get astronomical events for a given date.
        :param date: Datetime object representing the date for which to get astronomical events
        :return: Dictionary containing astronomical events for the given date
        """
        self.logger.info("Getting astronomical events...")
        events = {'visible_planets': self.visible_planets(date), 'conjunctions': self.check_conjunctions(date),
                  'meteor_showers': self.check_meteor_showers(date), 'moon_info': self.moon_info(date), 'sun_info': self.get_sun_info(date)}

        self.logger.info("Astronomical events retrieved successfully.")
        return events
