"""
Unit tests for business service layer.
"""

from unittest.mock import patch

from app.services import (
    zoning_service,
    tax_incentive_service,
    air_rights_service,
    property_service,
)


class TestZoningService:
    """Test zoning service functions."""

    def test_calculate_far_with_bonuses_no_bonuses(self, db_session):
        """Test FAR calculation without bonuses."""
        # Create test property and zoning
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "block_number": "123",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "building_area_sf": 5000.0,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        # Mock zoning analysis
        with patch(
            "app.services.zoning_service.analyze_property_zoning"
        ) as mock_analyze:
            mock_analyze.return_value = {
                "total_far_base": 10.0,
                "total_far_with_bonuses": 12.0,
            }

            far = zoning_service.calculate_far_with_bonuses(
                property_obj.id, include_bonuses=False, session=db_session
            )
            assert far == 10.0

            far_bonus = zoning_service.calculate_far_with_bonuses(
                property_obj.id, include_bonuses=True, session=db_session
            )
            assert far_bonus == 12.0

    def test_get_setback_requirements(self, db_session):
        """Test setback requirements retrieval."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        with patch(
            "app.services.zoning_service.analyze_property_zoning"
        ) as mock_analyze:
            mock_analyze.return_value = {
                "setback_requirements": {"front_ft": 10, "side_ft": 5, "rear_ft": 5}
            }

            setbacks = zoning_service.get_setback_requirements(
                property_obj.id, db_session
            )
            assert setbacks["front_ft"] == 10
            assert setbacks["side_ft"] == 5
            assert setbacks["rear_ft"] == 5


class TestTaxIncentiveService:
    """Test tax incentive service functions."""

    def test_check_tax_incentive_eligibility(self, db_session):
        """Test tax incentive eligibility checking."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        results = tax_incentive_service.check_tax_incentive_eligibility(
            property_obj.id, db_session
        )

        # Should return results for 467-M and ICAP
        assert len(results) >= 2
        program_codes = [r["program_code"] for r in results]
        assert "467-M" in program_codes
        assert "ICAP" in program_codes

    def test_estimate_tax_abatement_value(self, db_session):
        """Test tax abatement value estimation."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        # Test non-eligible program
        value = tax_incentive_service.estimate_tax_abatement_value(
            property_obj.id, "NONEXISTENT", db_session
        )
        assert value == 0

    def test_467m_eligibility_calculation(self, db_session):
        """Test 467-M eligibility calculation."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        result = tax_incentive_service.calculate_467m_eligibility(
            property_obj.id, db_session
        )

        # Should not be eligible due to zoning
        assert result["program_code"] == "467-M"
        assert not result["is_eligible"]


class TestAirRightsService:
    """Test air rights service functions."""

    def test_calculate_transferable_far(self, db_session):
        """Test transferable FAR calculation."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "building_area_sf": 4000.0,  # 4000 SF built
                "land_area_sf": 2500.0,  # 2500 SF lot
            },
            db_session,
        )

        # Mock zoning service to return FAR of 2.0
        with patch(
            "app.services.air_rights_service.calculate_far_with_bonuses"
        ) as mock_far:
            mock_far.return_value = 2.0  # FAR of 2.0 = 5000 SF max buildable

            transferable = air_rights_service.calculate_transferable_far(
                property_obj.id, db_session
            )

            # Current FAR used = 4000/2500 = 1.6
            # Max FAR = 2.0, so unused = 0.4
            expected_unused = 2.0 - (4000.0 / 2500.0)
            assert abs(transferable - expected_unused) < 0.01

    def test_analyze_air_rights(self, db_session):
        """Test comprehensive air rights analysis."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "building_area_sf": 4000.0,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        with patch(
            "app.services.air_rights_service.calculate_far_with_bonuses"
        ) as mock_far, patch(
            "app.services.air_rights_service.find_air_rights_recipients"
        ) as mock_recipients, patch(
            "app.services.air_rights_service.calculate_tdr_price"
        ) as mock_price:

            mock_far.return_value = 2.0
            mock_recipients.return_value = []
            mock_price.return_value = 125.00

            analysis = air_rights_service.analyze_air_rights(
                property_obj.id, db_session
            )

            assert analysis["property_id"] == str(property_obj.id)
            assert "unused_far" in analysis
            assert "transferable_far" in analysis
            assert "estimated_value" in analysis


class TestPropertyService:
    """Test property service functions."""

    def test_create_property(self, db_session):
        """Test property creation."""
        property_data = {
            "address": "123 Test St",
            "lot_number": "123-ABC",
            "block_number": "123",
            "zip_code": "10001",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "building_area_sf": 5000.0,
            "land_area_sf": 2500.0,
        }

        property_obj = property_service.create_property(property_data, db_session)

        assert property_obj.id is not None
        assert property_obj.address == property_data["address"]
        assert property_obj.lot_number == property_data["lot_number"]

    def test_get_property_full_analysis(self, db_session):
        """Test comprehensive property analysis."""
        property_obj = property_service.create_property(
            {
                "address": "123 Test St",
                "lot_number": "123-ABC",
                "zip_code": "10001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "land_area_sf": 2500.0,
            },
            db_session,
        )

        # Mock the service calls to avoid complex setup
        with patch(
            "app.services.property_service.zoning_service"
        ) as mock_zoning, patch(
            "app.services.property_service.tax_incentive_service"
        ) as mock_tax, patch(
            "app.services.property_service.air_rights_service"
        ) as mock_air, patch(
            "app.services.property_service.spatial_queries"
        ) as mock_spatial:

            mock_zoning.analyze_property_zoning.return_value = {"total_far": 10.0}
            mock_tax.check_tax_incentive_eligibility.return_value = []
            mock_air.analyze_air_rights.return_value = {"unused_far": 0}
            mock_spatial.find_nearby_landmarks.return_value = []

            analysis = property_service.get_property_full_analysis(
                property_obj.id, db_session
            )

            assert analysis["property"]["id"] == str(property_obj.id)
            assert "zoning" in analysis
            assert "tax_incentives" in analysis
            assert "air_rights" in analysis
            assert "nearby_landmarks" in analysis
