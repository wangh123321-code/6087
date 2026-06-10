import xml.etree.ElementTree as ET
import math
from typing import Optional
from app.models import GpxParseResult


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def parse_gpx(gpx_content: str) -> GpxParseResult:
    root = ET.fromstring(gpx_content)
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    trkpts = root.findall(f".//{ns}trkpt")
    if len(trkpts) < 2:
        return GpxParseResult(distance=0.0, duration=0, avg_pace=0.0, points_count=len(trkpts))

    total_distance = 0.0
    points = []

    for pt in trkpts:
        lat = float(pt.get("lat", 0))
        lon = float(pt.get("lon", 0))
        time_elem = pt.find(f"{ns}time")
        time_str = time_elem.text if time_elem is not None else None
        points.append({"lat": lat, "lon": lon, "time": time_str})

    for i in range(1, len(points)):
        total_distance += haversine(
            points[i - 1]["lat"], points[i - 1]["lon"],
            points[i]["lat"], points[i]["lon"]
        )

    distance_km = total_distance / 1000.0

    duration = 0
    if points[0]["time"] and points[-1]["time"]:
        from datetime import datetime
        try:
            t_start = datetime.fromisoformat(points[0]["time"].replace("Z", "+00:00"))
            t_end = datetime.fromisoformat(points[-1]["time"].replace("Z", "+00:00"))
            duration = int((t_end - t_start).total_seconds())
        except (ValueError, TypeError):
            duration = 0

    avg_pace = duration / distance_km if distance_km > 0 else 0.0

    return GpxParseResult(
        distance=round(distance_km, 2),
        duration=duration,
        avg_pace=round(avg_pace, 2),
        points_count=len(trkpts)
    )
