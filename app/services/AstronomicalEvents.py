from functools import lru_cache

from skyfield.api import load, Topos
from skyfield.almanac import find_discrete, risings_and_settings, moon_phases, MOON_PHASES
from datetime import datetime
from typing import Any
import logging
import os
import json


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
        self.eph = load('de430.bsp')
        self.location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        self.meteor_shower_data = self.load_meteor_shower_data()

    @lru_cache(maxsize=128)
    def visible_planets(self, date: datetime) -> list[dict[str, Any]]:
        """
        Find visible planets at a given date using barycenters and include their sky coordinates.
        :param date: Datetime object representing date for which to find visible planets
        :return: A list of dictionaries containing the name of the planet, the time it is visible, and its sky
        coordinates
        """
        self.logger.info("Calculating visible planets...")
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)
        f = risings_and_settings(self.eph, self.eph['sun'], self.location)
        times, is_rise = find_discrete(t0, t1, f)
        visible_planets = []
        for time, rise in zip(times, is_rise):
            if not rise:
                continue
            for planet_name, planet_barycenter in [('Mars', 'mars barycenter'), ('Venus', 'venus barycenter'),
                                                   ('Jupiter', 'jupiter barycenter'), ('Saturn', 'saturn barycenter'),
                                                   ('Mercury', 'mercury barycenter')]:
                planet = self.eph[planet_barycenter]
                astrometric = (self.eph['earth'] + self.location).at(time).observe(planet)
                alt, az, _ = astrometric.apparent().altaz()
                if alt.degrees > 0:
                    visible_planets.append(
                        {'planet': planet_name, 'time': time.utc_iso(), 'altitude': alt.degrees, 'azimuth': az.degrees})
        self.logger.info("Visible planets calculated successfully.")
        return visible_planets

    @lru_cache(maxsize=128)
    def check_conjunctions(self, date: datetime) -> list[tuple[str, str]]:
        """
        Check for planetary conjunctions at a given date using barycenters.
        :param date: Datetime object representing date for which to check conjunctions
        :return: List of tuples containing the names of the planets in conjunction and the time of the event
        """
        self.logger.info("Checking for planetary conjunctions...")
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)
        f = risings_and_settings(self.eph, self.eph['sun'], self.location)
        times, is_rise = find_discrete(t0, t1, f)
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
        print(moon_phase)

        self.logger.info("Moon information retrieved successfully.")
        return {'moonrise': moonrise, 'moonset': moonset, 'moon_phase': moon_phase}

    @lru_cache(maxsize=128)
    def get_astronomical_events(self, date: datetime) -> dict[str, Any]:
        """
        Get astronomical events for a given date.
        :param date: Datetime object representing the date for which to get astronomical events
        :return: Dictionary containing astronomical events for the given date
        """
        self.logger.info("Getting astronomical events...")
        events = {'visible_planets': self.visible_planets(date), 'conjunctions': self.check_conjunctions(date),
            'meteor_showers': self.check_meteor_showers(date), 'moon_info': self.moon_info(date)}
        self.logger.info("Astronomical events retrieved successfully.")
        return events
