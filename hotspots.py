
from math import radians, sin, cos, sqrt, atan2


def distance_meters(lat1, lon1, lat2, lon2):
    """Calculate approximate distance between two GPS points."""

    earth_radius = 6_371_000

    lat1, lon1, lat2, lon2 = map(
        radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return earth_radius * 2 * atan2(sqrt(a), sqrt(1 - a))


def find_hotspots(reports, radius_meters=500, min_reports=3):
    """
    Find areas containing several hazard reports.

    Each report must contain:
    latitude, longitude, and hazard_type.
    """

    hotspots = []

    for report in reports:
        nearby = [
            item for item in reports
            if distance_meters(
                report["latitude"],
                report["longitude"],
                item["latitude"],
                item["longitude"]
            ) <= radius_meters
        ]

        if len(nearby) >= min_reports:
            center_lat = sum(
                item["latitude"] for item in nearby
            ) / len(nearby)

            center_lon = sum(
                item["longitude"] for item in nearby
            ) / len(nearby)

            hotspot = {
                "latitude": round(center_lat, 6),
                "longitude": round(center_lon, 6),
                "report_count": len(nearby),
                "hazard_types": sorted({
                    item["hazard_type"] for item in nearby
                }),
                "hotspot_level": (
                    "HIGH" if len(nearby) >= 5 else "MEDIUM"
                )
            }

            # Avoid adding the same cluster repeatedly.
            if not any(
                distance_meters(
                    hotspot["latitude"],
                    hotspot["longitude"],
                    existing["latitude"],
                    existing["longitude"]
                ) <= radius_meters
                for existing in hotspots
            ):
                hotspots.append(hotspot)

    return hotspots


if __name__ == "__main__":
    # Example locations for testing only — not real reports.
    sample_reports = [
        {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "hazard_type": "pothole"
        },
        {
            "latitude": 28.6140,
            "longitude": 77.2091,
            "hazard_type": "pothole"
        },
        {
            "latitude": 28.6141,
            "longitude": 77.2092,
            "hazard_type": "waterlogging"
        },
        {
            "latitude": 28.6200,
            "longitude": 77.2200,
            "hazard_type": "pothole"
        }
    ]

    print("=== FLOODLENS HOTSPOT TEST ===")
    print(find_hotspots(sample_reports))
