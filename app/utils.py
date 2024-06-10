import logging
from timezonefinder import TimezoneFinder
from pytz import timezone


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


def configure_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])
