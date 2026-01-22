"""
Integration tests for API endpoints.
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client fixture."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns correct response."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "service" in data
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "docs" in data


class TestPropertyEndpoints:
    """Test property-related endpoints."""

    def test_analyze_property_missing_data(self, client):
        """Test property analysis with missing required data."""
        response = client.post("/api/properties/analyze", json={})
        assert response.status_code == 422  # Validation error

    def test_analyze_property_invalid_address(self, client):
        """Test property analysis with invalid address."""
        data = {
            "address": "",  # Empty address
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        response = client.post("/api/properties/analyze", json=data)
        assert response.status_code == 422  # Validation error

    def test_get_property_not_found(self, client):
        """Test getting non-existent property."""
        response = client.get("/api/properties/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_search_properties_empty_address(self, client):
        """Test property search with empty address."""
        response = client.get("/api/properties/search?address=")
        assert response.status_code == 422  # Validation error


class TestZoningEndpoints:
    """Test zoning-related endpoints."""

    def test_get_zoning_district_not_found(self, client):
        """Test getting non-existent zoning district."""
        response = client.get("/api/zoning/districts/NONEXISTENT")
        assert response.status_code == 404

    def test_calculate_far_invalid_input(self, client):
        """Test FAR calculation with invalid input."""
        data = {"lot_area_sf": -100, "zoning_codes": []}  # Negative area
        response = client.post("/api/zoning/far-calculator", json=data)
        assert response.status_code == 422  # Validation error

    def test_check_zoning_compliance_no_params(self, client):
        """Test zoning compliance check without required parameters."""
        response = client.get(
            "/api/properties/123e4567-e89b-12d3-a456-426614174000/zoning/compliance"
        )
        # Should return 404 for non-existent property
        assert response.status_code == 404


class TestLandmarkEndpoints:
    """Test landmark-related endpoints."""

    def test_get_nearby_landmarks_invalid_property(self, client):
        """Test getting landmarks for invalid property ID."""
        response = client.get("/api/properties/invalid-id/landmarks")
        assert response.status_code == 422  # UUID validation error

    def test_get_nearby_landmarks_not_found(self, client):
        """Test getting landmarks for non-existent property."""
        property_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/properties/{property_id}/landmarks")
        assert response.status_code == 404

    def test_get_landmarks_by_type_invalid_type(self, client):
        """Test getting landmarks with invalid type."""
        response = client.get("/api/landmarks/by-type?landmark_type=invalid")
        # Should return empty list for invalid type
        assert response.status_code == 200
        assert response.json() == []


class TestTaxIncentiveEndpoints:
    """Test tax incentive endpoints."""

    def test_check_tax_incentives_invalid_property(self, client):
        """Test checking incentives for invalid property."""
        response = client.get("/api/properties/invalid-id/tax-incentives")
        assert response.status_code == 422  # UUID validation error

    def test_get_tax_incentive_program_not_found(self, client):
        """Test getting non-existent tax incentive program."""
        response = client.get("/api/tax-incentives/programs/NONEXISTENT")
        assert response.status_code == 404


class TestAirRightsEndpoints:
    """Test air rights endpoints."""

    def test_analyze_air_rights_invalid_property(self, client):
        """Test analyzing air rights for invalid property."""
        response = client.get("/api/properties/invalid-id/air-rights")
        assert response.status_code == 422  # UUID validation error


class TestReportEndpoints:
    """Test report generation endpoints."""

    def test_generate_pdf_invalid_property(self, client):
        """Test PDF generation for invalid property."""
        data = {"property_id": "invalid-uuid", "include_zoning": True}
        response = client.post("/api/reports/generate-pdf", json=data)
        assert response.status_code == 422  # UUID validation error

    def test_preview_report_invalid_property(self, client):
        """Test report preview for invalid property."""
        data = {"property_id": "invalid-uuid"}
        response = client.post("/api/reports/preview", json=data)
        assert response.status_code == 422  # UUID validation error


class TestAPIValidation:
    """Test API input validation."""

    def test_uuid_validation(self, client):
        """Test UUID parameter validation."""
        invalid_uuids = [
            "not-a-uuid",
            "123",
            "",
            "123e4567-e89b-12d3-a456",  # Too short
        ]

        for invalid_uuid in invalid_uuids:
            response = client.get(f"/api/properties/{invalid_uuid}")
            assert response.status_code == 422

    def test_required_fields_validation(self, client):
        """Test required field validation."""
        # Test missing required address field
        response = client.post(
            "/api/properties/analyze",
            json={
                "latitude": 40.7128,
                "longitude": -74.0060,
                # Missing address
            },
        )
        assert response.status_code == 422

    def test_coordinate_bounds_validation(self, client):
        """Test coordinate bounds validation."""
        # Test invalid latitude
        response = client.post(
            "/api/properties/analyze",
            json={
                "address": "123 Test St",
                "latitude": 91,  # Invalid latitude
                "longitude": -74.0060,
            },
        )
        assert response.status_code == 422

        # Test invalid longitude
        response = client.post(
            "/api/properties/analyze",
            json={
                "address": "123 Test St",
                "latitude": 40.7128,
                "longitude": 181,  # Invalid longitude
            },
        )
        assert response.status_code == 422


class TestCORSHeaders:
    """Test CORS headers are present."""

    def test_cors_headers(self, client):
        """Test that CORS headers are included in responses."""
        response = client.options("/api/properties/search")
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
