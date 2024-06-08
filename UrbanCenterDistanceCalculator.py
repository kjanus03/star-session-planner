from geopy.distance import geodesic
from scipy.spatial import KDTree

class UrbanCenterDistanceCalculator:
    """
    Calculate the distance from a given location to the nearest urban center.
    """
    def __init__(self, latitude: float, longitude: float, urban_centers: list[dict]):
        """
        Initialize the UrbanCenterDistanceCalculator with a list of urban centers.
        :param urban_centers: A list of dictionaries containing the name, latitude, and longitude of urban centers
        """
        self.latitude = latitude
        self.longitude = longitude
        self.urban_centers = urban_centers
        self.coordinates = [(center['latitude'], center['longitude']) for center in urban_centers]
        self.kdtree = self.create_kdtree()


    def create_kdtree(self) -> KDTree:
        """
        Create a KDTree from the coordinates of urban centers.
        :return: A KDTree object
        """
        kdtree = KDTree(self.coordinates)
        return kdtree

    def distance_from_nearest_urban_center(self) -> tuple[float, dict]:
        """
        Calculate the distance from the given coordinates to the nearest urban center.
        :param latitude: Latitude of the location
        :param longitude: Longitude of the location
        :return: A tuple of the distance and the nearest urban center
        """
        distance, index = self.kdtree.query((self.latitude, self.longitude))
        nearest_center = self.urban_centers[index]
        # Calculate the precise geodesic distance
        precise_distance = geodesic((self.latitude, self.longitude), (nearest_center['latitude'], nearest_center['longitude'])).kilometers
        return precise_distance, nearest_center