"""
Pytest configuration and fixtures for testing.

Provides database sessions, test data, and common test utilities.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.config import Settings


@pytest.fixture(scope="session")
def test_settings():
    """Test application settings."""
    return Settings(
        database_url="sqlite:///:memory:",
        environment="testing",
        secret_key="test-secret-key",
        mapbox_token="test-mapbox-token",
    )


@pytest.fixture(scope="session")
def test_engine(test_settings):
    """Test database engine."""
    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    return engine


@pytest.fixture(scope="session")
def create_tables(test_engine):
    """Create all database tables for testing."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_engine, create_tables):
    """Database session fixture for tests."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_property_data():
    """Sample property data for testing."""
    return {
        "address": "123 Test St",
        "lot_number": "123-ABC",
        "block_number": "123",
        "zip_code": "10001",
        "building_area_sf": 5000.0,
        "land_area_sf": 2500.0,
        "current_use": "Residential",
    }


@pytest.fixture
def sample_zoning_district_data():
    """Sample zoning district data for testing."""
    return {
        "district_code": "R10",
        "district_name": "Residential 10",
        "far_base": 10.0,
        "far_with_bonus": 12.0,
        "max_height_ft": 150,
        "setback_requirements": {"front_ft": 10, "side_ft": 5, "rear_ft": 5},
        "building_class": "Residential",
    }


@pytest.fixture
def sample_landmark_data():
    """Sample landmark data for testing."""
    return {
        "name": "Test Historic Building",
        "landmark_type": "historic",
        "description": "A historic building in NYC",
    }


@pytest.fixture
def sample_tax_incentive_data():
    """Sample tax incentive data for testing."""
    return {
        "program_code": "467-M",
        "program_name": "Residential Conversion Tax Abatement",
        "description": "Tax abatement for converting commercial to residential",
        "eligible_zoning_districts": ["C4-7", "C6-4"],
        "min_building_age": 20,
        "requires_residential": True,
        "tax_abatement_years": 25,
    }


@pytest.fixture
def sample_air_rights_data():
    """Sample air rights data for testing."""
    return {"unused_far": 5.5, "transferable_far": 4.5, "tdr_price_per_sf": 125.00}


# Test data factories
def create_test_property(db_session: Session, **overrides):
    """Factory function to create test property."""
    from app.models import Property
    from geoalchemy2 import WKTElement

    data = {
        "address": "123 Test St",
        "lot_number": "123-ABC",
        "block_number": "123",
        "zip_code": "10001",
        "geom": WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        "building_area_sf": 5000.0,
        "land_area_sf": 2500.0,
        "current_use": "Residential",
    }
    data.update(overrides)

    property_obj = Property(**data)
    db_session.add(property_obj)
    db_session.commit()
    db_session.refresh(property_obj)
    return property_obj


def create_test_zoning_district(db_session: Session, **overrides):
    """Factory function to create test zoning district."""
    from app.models import ZoningDistrict
    from geoalchemy2 import WKTElement

    data = {
        "district_code": "R10",
        "district_name": "Residential 10",
        "geom": WKTElement(
            "MULTIPOLYGON(((-74.0100 40.7100, -74.0020 40.7100, -74.0020 40.7150, -74.0100 40.7150, -74.0100 40.7100)))",
            srid=4326,
        ),
        "far_base": 10.0,
        "far_with_bonus": 12.0,
        "max_height_ft": 150,
        "setback_requirements": {"front_ft": 10, "side_ft": 5, "rear_ft": 5},
        "building_class": "Residential",
    }
    data.update(overrides)

    district = ZoningDistrict(**data)
    db_session.add(district)
    db_session.commit()
    db_session.refresh(district)
    return district


def create_test_landmark(db_session: Session, **overrides):
    """Factory function to create test landmark."""
    from app.models import Landmark
    from geoalchemy2 import WKTElement

    data = {
        "name": "Test Historic Building",
        "landmark_type": "historic",
        "geom": WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        "description": "A historic building in NYC",
    }
    data.update(overrides)

    landmark = Landmark(**data)
    db_session.add(landmark)
    db_session.commit()
    db_session.refresh(landmark)
    return landmark


def create_test_property_zoning(
    db_session: Session, property_id, zoning_id, **overrides
):
    """Factory function to create test property-zoning relationship."""
    from app.models import PropertyZoning

    data = {
        "property_id": property_id,
        "zoning_district_id": zoning_id,
        "percent_in_district": 100.0,
    }
    data.update(overrides)

    relationship = PropertyZoning(**data)
    db_session.add(relationship)
    db_session.commit()
    db_session.refresh(relationship)
    return relationship


# Mock fixtures for external services
@pytest.fixture
def mock_geocoding_service():
    """Mock geocoding service."""

    class MockGeocodingService:
        async def geocode_address(self, address, city="New York", state="NY"):
            return (-74.0060, 40.7128)  # NYC center

        async def reverse_geocode(self, lat, lon):
            return {
                "full_address": "123 Test St, New York, NY 10001",
                "street": "123 Test St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
            }

    return MockGeocodingService()


@pytest.fixture
def mock_mapbox_client():
    """Mock Mapbox API client."""

    class MockMapboxClient:
        def get_street_address(self, coordinates):
            return "123 Test St, New York, NY 10001"

        def get_zoning_overlay(self, bounds):
            return {"type": "FeatureCollection", "features": []}

    return MockMapboxClient()


# Test configuration
def pytest_configure(config):
    """Pytest configuration hook."""
    # Set test environment
    os.environ.setdefault("ENVIRONMENT", "testing")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


def pytest_collection_modifyitems(config, items):
    """Modify test items for better organization."""
    for item in items:
        # Add markers based on test path
        if "test_models" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "test_services" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_spatial_queries" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
