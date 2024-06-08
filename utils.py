from timezonefinder import TimezoneFinder
from pytz import timezone
from geopy.distance import geodesic


def get_timezone_from_coordinates(latitude: float, longitude: float) -> timezone:
    """
    Get the timezone from the given coordinates.
    :param latitude:
    :param longitude:
    :return: Timezone object
    """
    tf = TimezoneFinder()
    # returns the timezone as a string (the format accepted by Open-Meteo API, e.g., 'Europe/Berlin'
    tz_str = tf.timezone_at(lat=latitude, lng=longitude)
    if tz_str is None:
        return None
    tz = timezone(tz_str)
    return tz

