from skyfield.api import load, Topos
from datetime import datetime
from skyfield.almanac import find_discrete, risings_and_settings
from typing import List, Dict, Tuple, Any


class AstronomicalEvents:
    """
    Class for finding astronomical events like visible planets, conjunctions, and meteor showers.
    """

    def __init__(self, latitude: float, longitude: float):
        """
        Constructor for the AstronomicalEvents class.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        """
        self.ts = load.timescale()
        self.eph = load('de430.bsp')
        self.location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    def visible_planets(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Find visible planets at a given date using barycenters and include their sky coordinates.
        :param date: Datetime object representing date for which to find visible planets
        :return: A list of dictionaries containing the name of the planet, the time it is visible, and its sky coordinates
        """
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)
        f = risings_and_settings(self.eph, self.eph['sun'], self.location)
        times, is_rise = find_discrete(t0, t1, f)
        visible_planets = []
        for time, rise in zip(times, is_rise):
            if not rise:
                continue
            for planet_name, planet_barycenter in [('Mars', 'mars barycenter'),
                                                   ('Venus', 'venus barycenter'),
                                                   ('Jupiter', 'jupiter barycenter'),
                                                   ('Saturn', 'saturn barycenter'),
                                                   ('Mercury', 'mercury barycenter')]:
                planet = self.eph[planet_barycenter]
                astrometric = (self.eph['earth'] + self.location).at(time).observe(planet)
                alt, az, _ = astrometric.apparent().altaz()
                if alt.degrees > 0:
                    visible_planets.append({
                        'planet': planet_name,
                        'time': time.utc_iso(),
                        'altitude': alt.degrees,
                        'azimuth': az.degrees
                    })
        return visible_planets

    def check_conjunctions(self, date: datetime) -> List[Tuple[str, str]]:
        """
        Check for planetary conjunctions at a given date using barycenters.
        :param date: Datetime object representing date for which to check conjunctions
        :return: List of tuples containing the names of the planets in conjunction and the time of the event
        """
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day, 23, 59, 59)
        f = risings_and_settings(self.eph, self.eph['sun'], self.location)
        times, is_rise = find_discrete(t0, t1, f)
        conjunctions = []
        for time, rise in zip(times, is_rise):
            if not rise:
                continue
            for planet1_name, planet1_barycenter in [('Mars', 'mars barycenter'),
                                                     ('Venus', 'venus barycenter'),
                                                     ('Jupiter', 'jupiter barycenter'),
                                                     ('Saturn', 'saturn barycenter'),
                                                     ('Mercury', 'mercury barycenter')]:
                for planet2_name, planet2_barycenter in [('Mars', 'mars barycenter'),
                                                         ('Venus', 'venus barycenter'),
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
        return conjunctions

    def check_meteor_showers(self, date: datetime) -> List[str]:
        """
        Check for meteor showers at a given date.
        :param date: Datetime object representing date for which to check meteor showers
        :return: List of meteor showers active on the given date
        """
        meteor_showers = {
            'Quadrantids': {'start': (1, 1), 'end': (1, 5), 'peak': [(1, 3)]},
            'Lyrids': {'start': (4, 16), 'end': (4, 25), 'peak': [(4, 22)]},
            'Eta Aquariids': {'start': (4, 19), 'end': (5, 28), 'peak': [(5, 6)]},
            'Delta Aquariids': {'start': (7, 12), 'end': (8, 23), 'peak': [(7, 28), (7, 29), (7, 30)]},
            'Perseids': {'start': (7, 17), 'end': (8, 24), 'peak': [(8, 12), (8, 13)]},
            'Orionids': {'start': (10, 2), 'end': (11, 7), 'peak': [(10, 21)]},
            'Leonids': {'start': (11, 6), 'end': (11, 30), 'peak': [(11, 17)]},
            'Geminids': {'start': (12, 4), 'end': (12, 17), 'peak': [(12, 13), (12, 14)]},
            'Ursids': {'start': (12, 17), 'end': (12, 26), 'peak': [(12, 22)]}
        }

        showers = []
        for name, info in meteor_showers.items():
            start_date = datetime(date.year, *info['start'])
            end_date = datetime(date.year, *info['end'])
            if start_date <= date <= end_date:
                showers.append(name)
        return showers

    def get_astronomical_events(self, date: datetime) -> Dict[str, Any]:
        """
        Get astronomical events for a given date.
        :param date: Datetime object representing the date for which to get astronomical events
        :return: Dictionary containing astronomical events for the given date
        """
        events = {
            'visible_planets': self.visible_planets(date),
            'conjunctions': self.check_conjunctions(date),
            'meteor_showers': self.check_meteor_showers(date)
        }
        return events

