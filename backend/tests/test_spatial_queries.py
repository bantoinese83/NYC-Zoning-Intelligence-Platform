"""
Unit tests for spatial query functions.
"""

import pytest
from unittest.mock import patch
from geoalchemy2 import WKTElement

from app.services import spatial_queries


class TestSpatialQueries:
    """Test spatial query functions."""

    def test_find_zoning_districts_no_districts(self, db_session):
        """Test finding zoning districts when none exist."""
        geom = WKTElement("POINT(-74.0060 40.7128)", srid=4326)
        districts = spatial_queries.find_zoning_districts(geom, db_session)
        assert districts == []

    def test_calculate_far_no_zoning(self, db_session):
        """Test FAR calculation when no zoning districts found."""
        # This would require mocking the spatial query
        with patch("app.services.spatial_queries.find_zoning_districts") as mock_find:
            mock_find.return_value = []

            result = spatial_queries.calculate_far(
                "test-property-id", [], False, db_session
            )

            # Should return default/empty result
            assert result["far_effective"] == 0

    def test_find_nearby_landmarks_no_landmarks(self, db_session):
        """Test finding landmarks when none exist near property."""
        with patch(
            "app.services.spatial_queries.get_property_centroid"
        ) as mock_centroid:
            mock_centroid.return_value = (-74.0060, 40.7128)

            landmarks = spatial_queries.find_nearby_landmarks(
                "test-property-id", 150, db_session
            )

            assert landmarks == []

    def test_get_property_centroid_invalid_property(self, db_session):
        """Test getting centroid for non-existent property."""
        with pytest.raises(ValueError, match="Property .* not found"):
            spatial_queries.get_property_centroid("non-existent-id", db_session)

    def test_calculate_distance(self):
        """Test distance calculation between coordinates."""
        from app.utils.geocoding import calculate_distance

        # Test distance between same point
        distance = calculate_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert distance == 0

        # Test distance between two points (approximately)
        # NYC to Boston is about 215 miles = 346,000 meters
        distance = calculate_distance(40.7128, -74.0060, 42.3601, -71.0589)
        assert distance > 340000  # Approximately 346km
        assert distance < 350000

    def test_validate_nyc_coordinates(self):
        """Test NYC coordinate validation."""
        from app.utils.geocoding import validate_nyc_coordinates

        # Valid NYC coordinates
        assert validate_nyc_coordinates(40.7128, -74.0060) is True

        # Invalid coordinates (outside NYC)
        assert validate_nyc_coordinates(35.0, -80.0) is False  # Charlotte, NC
        assert validate_nyc_coordinates(41.5, -74.0) is False  # Too far north
        assert validate_nyc_coordinates(40.7, -72.0) is False  # Too far east

    def test_coordinates_to_bbox(self):
        """Test bounding box calculation from coordinates."""
        from app.utils.geocoding import coordinates_to_bbox

        lat, lon = 40.7128, -74.0060
        distance = 1000  # 1km

        min_lon, min_lat, max_lon, max_lat = coordinates_to_bbox(lat, lon, distance)

        # Check that bbox contains original point
        assert min_lon < lon < max_lon
        assert min_lat < lat < max_lat

        # Check that bbox has reasonable size
        assert abs(max_lon - min_lon) > 0
        assert abs(max_lat - min_lat) > 0

    def test_batch_distance_calculation_empty_list(self, db_session):
        """Test batch distance calculation with empty target list."""
        geom = WKTElement("POINT(-74.0060 40.7128)", srid=4326)
        results = spatial_queries.batch_distance_calculation(geom, [], db_session)
        assert results == []

    def test_get_zoning_summary_invalid_property(self, db_session):
        """Test zoning summary for invalid property."""
        with pytest.raises(ValueError, match="Property .* not found"):
            spatial_queries.get_zoning_summary("non-existent-id", db_session)
