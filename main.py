from OpenElevationClient import OpenElevationClient
from OpenMeteoClient import OpenMeteoClient
from OpenStreetMapClient import OpenStreetMapClient


def main():
    latitude, longitude = 52.473, 13.403
    osm_client = OpenStreetMapClient(latitude=latitude, longitude=longitude)
    terrain_types = osm_client.fetch_terrain_type()
    print(f"Terrain types at {latitude}, {longitude}: {terrain_types}")

    elevation_client = OpenElevationClient(latitude=latitude, longitude=longitude)  # Example location (Berlin, Germany)
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
