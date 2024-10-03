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


def configure_logging() -> None:
    """
    Configure logging for the application.
    :return:
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("../app.log"), logging.StreamHandler()], encoding='utf-8')


def convert_bytes_to_str(data: any):
    """
    Convert any bytes objects to strings in the data structure.
    :param data:
    :return:
    """
    if isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, dict):
        return {k: convert_bytes_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_bytes_to_str(i) for i in data]
    return data

def get_cloud_cover_emoji(cloud_cover: float) -> str:
    """
    Returns an emoji representing the cloud cover.
    :param cloud_cover: The cloud cover percentage
    :return: A string with the appropriate emoji
    """
    logging.info(f"Getting cloud cover emoji")
    if cloud_cover <= 25:
        return "☀️"
    elif cloud_cover <= 50:
        return "🌤️"
    elif cloud_cover <= 75:
        return "⛅"
    else:
        return "☁️"
