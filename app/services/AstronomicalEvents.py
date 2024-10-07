from functools import lru_cache

from skyfield.api import load, Topos
from skyfield.almanac import find_discrete, risings_and_settings, moon_phases
from datetime import datetime
from typing import Any
import logging


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

    @lru_cache(maxsize=128)
    def check_meteor_showers(self, date: datetime) -> list[dict[str, Any]]:
        """
        Check for meteor showers at a given date.
        :param date: Datetime object representing date for which to check meteor showers
        :return: List of meteor showers active on the given date
        """
        self.logger.info("Checking for meteor showers...")
        year = date.year
        meteor_showers = {'Quadrantids': {'start': (year, 1, 1), 'end': (year, 1, 5), 'peak': [(year, 1, 3)]},
            'Lyrids': {'start': (year, 4, 16), 'end': (year, 4, 25), 'peak': [(year, 4, 22)]},
            'Eta Aquariids': {'start': (year, 4, 19), 'end': (year, 5, 28), 'peak': [(year, 5, 6)]},
            'Delta Aquariids': {'start': (year, 7, 12), 'end': (year, 8, 23), 'peak': [(year, 7, 28), (year, 7, 29), (year, 7, 30)]},
            'Perseids': {'start': (year, 7, 17), 'end': (year, 8, 24), 'peak': [(year, 8, 12), (year, 8, 13)]},
            'Orionids': {'start': (year, 10, 2), 'end': (year, 11, 7), 'peak': [(year, 10, 21)]},
            'Leonids': {'start': (year, 11, 6), 'end': (year, 11, 30), 'peak': [(year, 11, 17)]},
            'Geminids': {'start': (year, 12, 4), 'end': (year, 12, 17), 'peak': [(year, 12, 13), (year, 12, 14)]},
            'Ursids': {'start': (year, 12, 17), 'end': (year, 12, 26), 'peak': [(year, 12, 22)]}}

        showers = []
        for name, info in meteor_showers.items():
            start_date = datetime(*info['start'])
            end_date = datetime(*info['end'])
            if start_date <= date <= end_date:
                shower_info =  meteor_showers[name]
                shower_info['name'] = name

                showers.append(meteor_showers[name])
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
        moon_phase_times, moon_phases_list = find_discrete(t0, t1, moon_phases(self.eph))

        moonrise = None
        moonset = None
        for time, rise in zip(moonrise_set_times, is_moonrise):
            if rise:
                moonrise = time.utc_iso()
            else:
                moonset = time.utc_iso()

        moon_phase = None
        for time, phase in zip(moon_phase_times, moon_phases_list):
            if t0.tt <= time.tt <= t1.tt:
                moon_phase = phase


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
