import datetime

from Clients.OpenElevationClient import OpenElevationClient
from Clients.OpenMeteoClient import OpenMeteoClient
from Clients.OpenStreetMapClient import OpenStreetMapClient
from UrbanCenterDistanceCalculator import UrbanCenterDistanceCalculator
from AstronomicalEvents import AstronomicalEvents
from utils import configure_logging

def main():
    latitude, longitude = 51.5518, 15.3354
    osm_client = OpenStreetMapClient(latitude=latitude, longitude=longitude)
    terrain_types = osm_client.fetch_terrain_type()
    print(f"Terrain types at {latitude}, {longitude}: {terrain_types}")

    elevation_client = OpenElevationClient(latitude=latitude, longitude=longitude)
    elevation = elevation_client.fetch_elevation()
    print(f"Elevation at {latitude}, {longitude}: {elevation} meters")

    open_meteo_client = OpenMeteoClient(latitude=latitude, longitude=longitude)
    print(open_meteo_client)
    open_meteo_client.fetch_weather_data()

    location_info = open_meteo_client.get_location_info()
    print(location_info)

    current_weather = open_meteo_client.get_current_weather()
    print(current_weather)

    hourly_weather = open_meteo_client.get_hourly_weather()
    print(hourly_weather)

    daily_weather = open_meteo_client.get_daily_weather()
    print(daily_weather)

    bbox = "51.354690,14.869034,51.830811,15.850018"  # Example bounding box
    urban_centers = osm_client.fetch_urban_centers(bbox)
    print(urban_centers)

    ucdc = UrbanCenterDistanceCalculator(latitude, longitude, urban_centers)
    distance, center = ucdc.distance_from_nearest_urban_center()
    print(f"Distance from nearest urban center: {distance} km")
    print(f"Nearest urban center: {center}")

    astronomical_events = AstronomicalEvents(latitude, longitude)
    date = datetime.datetime.today()
    print(f"Astronomical events for {date.date()}: {astronomical_events.get_astronomical_events(date)}")


if __name__ == '__main__':
    configure_logging()
    main()

