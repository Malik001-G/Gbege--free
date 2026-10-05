import math

def haversine_distance(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """
    Computes straight-line great-circle distance between two (lat, lon) coordinates in meters.
    Admissible for road networks because Euclidean/Haversine distance <= true driving distance.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371000.0  # Earth's radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c