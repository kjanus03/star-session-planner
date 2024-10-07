from flask import Blueprint, render_template, request, jsonify

from app.clients.NominatimClient import NominatimClient
from app.clients.OpenElevationClient import OpenElevationClient
from app.clients.OpenMeteoClient import OpenMeteoClient
from app.clients.OpenStreetMapClient import OpenStreetMapClient
from app.services.UrbanCenterDistanceCalculator import UrbanCenterDistanceCalculator
from app.services.AstronomicalEvents import AstronomicalEvents
from app.utilities.JSONFormatter import JSONFormatter
from app.utilities.utils import convert_bytes_to_str
from app.forms import CityForm
import datetime
import logging

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = CityForm()  # Create a form instance

    if form.validate_on_submit():
        city = form.city.data
        coordinates = get_coordinates_from_city(city)  # Convert city to lat/lon
        if coordinates:
            # Process coordinates with city and return JSON for AJAX
            return process_coordinates_with_city(coordinates['latitude'], coordinates['longitude'])
        else:
            return jsonify({"error": f"City '{city}' not found."}), 404

    return render_template('index.html', form=form)


def get_coordinates_from_city(city_name):
    nominatim_client = NominatimClient()
    return nominatim_client.get_lat_lon(city_name)

# Create a wrapper function to process coordinates from the city form
def process_coordinates_with_city(latitude, longitude):
    # This reuses the process_coordinates logic with latitude and longitude from the form
    return process_coordinates_with_lat_lon(latitude, longitude)

def process_coordinates_with_lat_lon(latitude, longitude):
    try:
        # You can reuse most of the logic from your process_coordinates function
        terrain_types = get_terrain_types(latitude, longitude)
        elevation = get_elevation(latitude, longitude)
        weather_data = get_weather_data(latitude, longitude)
        urban_centers, distance, nearest_center = get_urban_centers(latitude, longitude)
        astronomical_events = get_astronomical_events(latitude, longitude)

        result = {
            'terrain_types': terrain_types,
            'elevation': elevation,
            **weather_data,
            'urban_centers': urban_centers,
            'distance_from_urban_center': distance,
            'nearest_urban_center': nearest_center,
            'astronomical_events': astronomical_events
        }

        result = convert_bytes_to_str(result)
        formatter = JSONFormatter(result)
        formatted_result = formatter.format()

        return jsonify({'formatted_result': formatted_result, 'data': result})

    except Exception as e:
        logging.error(f"Error processing coordinates: {e}")
        return jsonify({"error": str(e)}), 500



@main.route('/process_coordinates', methods=['POST'])
def process_coordinates():
    try:
        data = request.get_json()
        latitude, longitude = data['latitude'], data['longitude']

        terrain_types = get_terrain_types(latitude, longitude)
        elevation = get_elevation(latitude, longitude)
        weather_data = get_weather_data(latitude, longitude)
        urban_centers, distance, nearest_center = get_urban_centers(latitude, longitude)
        astronomical_events = get_astronomical_events(latitude, longitude)

        result = {
            'terrain_types': terrain_types,
            'elevation': elevation,
            **weather_data,
            'urban_centers': urban_centers,
            'distance_from_urban_center': distance,
            'nearest_urban_center': nearest_center,
            'astronomical_events': astronomical_events
        }

        # Convert any bytes objects to strings
        result = convert_bytes_to_str(result)
        logging.info(f"Converted byte objects to string for JSON serialization")

        formatter = JSONFormatter(result)
        formatted_result = formatter.format()
        logging.info(f"Formatted JSON response correctly")


        return jsonify({'formatted_result': formatted_result, 'data': result})

    except Exception as e:
        logging.error(f"Error processing coordinates: {e}")
        return jsonify({"error": str(e)}), 500


def get_terrain_types(latitude, longitude):
    osm_client = OpenStreetMapClient(latitude=latitude, longitude=longitude)
    return osm_client.fetch_terrain_type()


def get_elevation(latitude, longitude):
    elevation_client = OpenElevationClient(latitude=latitude, longitude=longitude)
    return elevation_client.fetch_elevation()


def get_weather_data(latitude, longitude):
    open_meteo_client = OpenMeteoClient(latitude=latitude, longitude=longitude)
    open_meteo_client.fetch_weather_data()

    return {'location_info': open_meteo_client.get_location_info(),
        'current_weather': open_meteo_client.get_current_weather(),
        'hourly_weather': open_meteo_client.get_hourly_weather().to_dict(orient='records'),
        'daily_weather': open_meteo_client.get_daily_weather().to_dict(orient='records')}


def get_urban_centers(latitude, longitude, radius_km=25):
    osm_client = OpenStreetMapClient(latitude=latitude, longitude=longitude)
    urban_centers = osm_client.fetch_urban_centers(radius_km=radius_km)

    if not urban_centers:
        raise ValueError("No urban centers found within the bounding box.")

    ucdc = UrbanCenterDistanceCalculator(latitude, longitude, urban_centers)
    distance, nearest_center = ucdc.distance_from_nearest_urban_center()
    return urban_centers, distance, nearest_center


def get_astronomical_events(latitude, longitude):
    astronomical_events = AstronomicalEvents(latitude, longitude)
    date = datetime.datetime.today()
    return astronomical_events.get_astronomical_events(date)
