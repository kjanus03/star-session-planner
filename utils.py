from timezonefinder import TimezoneFinder
from pytz import timezone


def get_timezone_from_coordinates(lat, lng):
    tf = TimezoneFinder()
    # returns the timezone as a string (the format accepted by Open-Meteo API, e.g., 'Europe/Berlin'
    tz_str = tf.timezone_at(lat=lat, lng=lng)
    if tz_str is None:
        return None
    tz = timezone(tz_str)
    return tz
