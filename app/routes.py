from flask import Blueprint, render_template, request, jsonify
from app.clients.OpenElevationClient import OpenElevationClient
from app.clients.OpenMeteoClient import OpenMeteoClient
from app.clients.OpenStreetMapClient import OpenStreetMapClient
from app.services.UrbanCenterDistanceCalculator import UrbanCenterDistanceCalculator
from app.services.AstronomicalEvents import AstronomicalEvents
import datetime
import logging

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/process_coordinates', methods=['POST'])
def process_coordinates():
    logging.info("Hit the process_coordinates route")
    try:
        data = request.get_json()
        latitude = data['latitude']
        longitude = data['longitude']

        logging.info(f"Processing coordinates: latitude={latitude}, longitude={longitude}")

        osm_client = OpenStreetMapClient(latitude=latitude, longitude=longitude)
        terrain_types = osm_client.fetch_terrain_type()
        logging.info(f"Terrain types: {terrain_types}")

        elevation_client = OpenElevationClient(latitude=latitude, longitude=longitude)
        elevation = elevation_client.fetch_elevation()
        logging.info(f"Elevation: {elevation} meters")

        open_meteo_client = OpenMeteoClient(latitude=latitude, longitude=longitude)
        open_meteo_client.fetch_weather_data()

        location_info = open_meteo_client.get_location_info()
        logging.info(f"Location info: {location_info}")

        current_weather = open_meteo_client.get_current_weather()
        hourly_weather = open_meteo_client.get_hourly_weather().to_dict(orient='records')
        daily_weather = open_meteo_client.get_daily_weather().to_dict(orient='records')
        logging.info(f"Current weather: {current_weather}")
        logging.info(f"Hourly weather: {hourly_weather}")
        logging.info(f"Daily weather: {daily_weather}")

        urban_centers = osm_client.fetch_urban_centers(radius_km=20)
        logging.info(f"Fetched urban centers: {urban_centers}")

        if not urban_centers:
            logging.error("No urban centers found within the bounding box.")
            return jsonify({"error": "No urban centers found within the bounding box."}), 400

        ucdc = UrbanCenterDistanceCalculator(latitude, longitude, urban_centers)
        distance, center = ucdc.distance_from_nearest_urban_center()
        logging.info(f"Distance from nearest urban center: {distance} km")
        logging.info(f"Nearest urban center: {center}")

        astronomical_events = AstronomicalEvents(latitude, longitude)
        date = datetime.datetime.today()
        events = astronomical_events.get_astronomical_events(date)
        logging.info(f"Astronomical events: {events}")

        # Convert datetime objects to strings and handle bytes
        def convert_json_serializable(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            if isinstance(obj, bytes):
                return obj.decode()  # Assuming UTF-8 encoding
            if isinstance(obj, dict):
                return {key: convert_json_serializable(value) for key, value in obj.items()}
            if isinstance(obj, list):
                return [convert_json_serializable(item) for item in obj]
            return obj

        result = {'terrain_types': terrain_types, 'elevation': elevation, 'location_info': location_info,
            'current_weather': current_weather, 'hourly_weather': hourly_weather, 'daily_weather': daily_weather,
            'urban_centers': urban_centers, 'distance_from_urban_center': distance, 'nearest_urban_center': center,
            'astronomical_events': convert_json_serializable(events)}

        result = convert_json_serializable(result)
        logging.info(f"Result: {result}")

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error processing coordinates: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
