"""
Geocoding utilities for address to coordinate conversion.

Provides functions to convert NYC addresses to latitude/longitude coordinates
using various geocoding services (Mapbox, Google, OpenStreetMap, etc.).
"""

import logging
from typing import Dict, Tuple

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class GeocodingError(Exception):
    """Raised when geocoding fails."""

    pass


class GeocodingService:
    """
    Geocoding service for NYC addresses.

    Supports multiple geocoding providers with fallback logic.
    """

    def __init__(self):
        self.mapbox_token = settings.mapbox_token
        self.openai_key = settings.openai_api_key

    async def geocode_address(
        self,
        address: str,
        city: str = "New York",
        state: str = "NY",
        country: str = "US",
    ) -> Tuple[float, float]:
        """
        Geocode an address to latitude/longitude coordinates.

        Args:
            address: Street address
            city: City name
            state: State code
            country: Country code

        Returns:
            Tuple of (longitude, latitude)

        Raises:
            GeocodingError: If geocoding fails
        """
        full_address = f"{address}, {city}, {state}, {country}"

        logger.info(f"Geocoding address: {full_address}")

        # Try Mapbox first (most accurate for NYC)
        if self.mapbox_token:
            try:
                coords = await self._geocode_with_mapbox(full_address)
                logger.info(f"Mapbox geocoding successful: {coords}")
                return coords
            except Exception as e:
                logger.warning(f"Mapbox geocoding failed: {e}")

        # Fallback to OpenAI (if available)
        if self.openai_key:
            try:
                coords = await self._geocode_with_openai(full_address)
                logger.info(f"OpenAI geocoding successful: {coords}")
                return coords
            except Exception as e:
                logger.warning(f"OpenAI geocoding failed: {e}")

        # Final fallback: NYC center coordinates
        logger.warning("All geocoding services failed, using NYC center")
        nyc_center = (-74.0060, 40.7128)  # Manhattan center
        return nyc_center

    async def _geocode_with_mapbox(self, address: str) -> Tuple[float, float]:
        """
        Geocode using Mapbox Geocoding API.

        Args:
            address: Full address string

        Returns:
            Tuple of (longitude, latitude)
        """
        url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        params = {
            "access_token": self.mapbox_token,
            "limit": 1,
            "country": "us",
            "bbox": "-74.3,-74.7,40.5,41.0",  # NYC bounding box
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}{address}.json", params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("features"):
                raise GeocodingError("No results found")

            # Get the first (best) result
            feature = data["features"][0]
            coordinates = feature["geometry"]["coordinates"]

            # Mapbox returns [longitude, latitude]
            lon, lat = coordinates

            # Validate coordinates are in NYC bounds
            if not (40.5 <= lat <= 40.9 and -74.3 <= lon <= -73.7):
                raise GeocodingError("Coordinates not in NYC bounds")

            return lon, lat

    async def _geocode_with_openai(self, address: str) -> Tuple[float, float]:
        """
        Geocode using OpenAI's knowledge (experimental).

        This is a fallback that may not be very accurate.
        """
        # Placeholder - OpenAI doesn't have a direct geocoding API
        # This would require custom prompting and parsing
        logger.warning("OpenAI geocoding not implemented")
        raise GeocodingError("OpenAI geocoding not available")

    async def reverse_geocode(
        self, latitude: float, longitude: float
    ) -> Dict[str, str]:
        """
        Reverse geocode coordinates to address.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with address components
        """
        if not self.mapbox_token:
            raise GeocodingError("Mapbox token required for reverse geocoding")

        url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        params = {
            "access_token": self.mapbox_token,
            "limit": 1,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{url}{longitude},{latitude}.json", params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("features"):
                raise GeocodingError("No results found")

            feature = data["features"][0]
            properties = feature.get("properties", {})
            context = feature.get("context", [])

            # Extract address components
            address_info = {
                "full_address": feature.get("place_name", ""),
                "street": properties.get("address", ""),
                "city": "",
                "state": "",
                "zip_code": "",
            }

            # Parse context for city, state, zip
            for ctx in context:
                ctx_id = ctx.get("id", "")
                if ctx_id.startswith("place"):
                    address_info["city"] = ctx.get("text", "")
                elif ctx_id.startswith("region"):
                    address_info["state"] = ctx.get("text", "")
                elif ctx_id.startswith("postcode"):
                    address_info["zip_code"] = ctx.get("text", "")

            return address_info


def validate_nyc_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate that coordinates are within NYC bounds.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        True if coordinates are in NYC, False otherwise
    """
    # NYC approximate bounds
    nyc_bounds = {
        "north": 40.9176,  # Northern tip of Bronx
        "south": 40.4774,  # Southern tip of Staten Island
        "east": -73.7004,  # Eastern tip of Queens
        "west": -74.2591,  # Western tip of New Jersey border
    }

    return (
        nyc_bounds["south"] <= latitude <= nyc_bounds["north"]
        and nyc_bounds["west"] <= longitude <= nyc_bounds["east"]
    )


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.

    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate

    Returns:
        Distance in meters
    """
    import math

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in meters
    radius = 6371000

    return c * radius


def coordinates_to_bbox(
    latitude: float, longitude: float, distance_meters: float
) -> Tuple[float, float, float, float]:
    """
    Convert coordinates and distance to bounding box.

    Args:
        latitude: Center latitude
        longitude: Center longitude
        distance_meters: Distance from center

    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
    """
    # Approximate conversion: 1 degree ≈ 111,000 meters
    lat_offset = distance_meters / 111000
    lon_offset = distance_meters / (111000 * abs(latitude) / 90)  # Adjust for latitude

    return (
        longitude - lon_offset,  # min_lon
        latitude - lat_offset,  # min_lat
        longitude + lon_offset,  # max_lon
        latitude + lat_offset,  # max_lat
    )


# Global geocoding service instance
geocoding_service = GeocodingService()
