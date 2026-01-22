"""
Unit tests for SQLAlchemy models.
"""

from geoalchemy2 import WKTElement

from app.models import (
    Property,
    ZoningDistrict,
    PropertyZoning,
    Landmark,
    TaxIncentiveProgram,
    PropertyTaxIncentive,
    AirRights,
)


class TestPropertyModel:
    """Test Property model."""

    def test_property_creation(self, db_session, sample_property_data):
        """Test creating a property."""
        property_obj = Property(**sample_property_data)
        db_session.add(property_obj)
        db_session.commit()

        assert property_obj.id is not None
        assert property_obj.address == sample_property_data["address"]
        assert property_obj.lot_number == sample_property_data["lot_number"]

    def test_property_repr(self, sample_property_data):
        """Test property string representation."""
        property_obj = Property(**sample_property_data)
        repr_str = repr(property_obj)
        assert "Property" in repr_str
        assert sample_property_data["address"] in repr_str

    def test_property_to_dict(self, sample_property_data):
        """Test property serialization."""
        property_obj = Property(**sample_property_data)
        data = property_obj.to_dict()

        assert data["address"] == sample_property_data["address"]
        assert data["lot_number"] == sample_property_data["lot_number"]
        assert "id" in data
        assert "created_at" in data


class TestZoningDistrictModel:
    """Test ZoningDistrict model."""

    def test_zoning_district_creation(self, db_session):
        """Test creating a zoning district."""
        geom = WKTElement(
            "MULTIPOLYGON(((-74.0100 40.7100, -74.0020 40.7100, -74.0020 40.7150, -74.0100 40.7150, -74.0100 40.7100)))",
            srid=4326,
        )

        district = ZoningDistrict(
            district_code="R10",
            district_name="Residential 10",
            geom=geom,
            far_base=10.0,
            far_with_bonus=12.0,
            max_height_ft=150,
            setback_requirements={"front_ft": 10, "side_ft": 5, "rear_ft": 5},
            building_class="Residential",
        )

        db_session.add(district)
        db_session.commit()

        assert district.id is not None
        assert district.district_code == "R10"
        assert district.far_base == 10.0

    def test_zoning_district_repr(self):
        """Test zoning district string representation."""
        geom = WKTElement("MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))", srid=4326)
        district = ZoningDistrict(district_code="R10", far_base=10.0, geom=geom)

        repr_str = repr(district)
        assert "ZoningDistrict" in repr_str
        assert "R10" in repr_str

    def test_zoning_district_to_dict(self):
        """Test zoning district serialization."""
        geom = WKTElement("MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))", srid=4326)
        district = ZoningDistrict(
            district_code="R10",
            district_name="Residential 10",
            far_base=10.0,
            geom=geom,
        )

        data = district.to_dict()
        assert data["district_code"] == "R10"
        assert data["far_base"] == 10.0
        assert "id" in data


class TestPropertyZoningModel:
    """Test PropertyZoning junction model."""

    def test_property_zoning_creation(self, db_session):
        """Test creating property-zoning relationship."""
        # Create test property and zoning district first
        property_obj = Property(
            address="123 Test St",
            lot_number="123-ABC",
            land_area_sf=2500.0,
            geom=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )
        db_session.add(property_obj)

        geom = WKTElement("MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1, 0 0)))", srid=4326)
        district = ZoningDistrict(district_code="R10", far_base=10.0, geom=geom)
        db_session.add(district)
        db_session.commit()

        # Create relationship
        relationship = PropertyZoning(
            property_id=property_obj.id,
            zoning_district_id=district.id,
            percent_in_district=100.0,
        )
        db_session.add(relationship)
        db_session.commit()

        assert relationship.id is not None
        assert relationship.property_id == property_obj.id
        assert relationship.zoning_district_id == district.id
        assert relationship.percent_in_district == 100.0


class TestLandmarkModel:
    """Test Landmark model."""

    def test_landmark_creation(self, db_session, sample_landmark_data):
        """Test creating a landmark."""
        landmark = Landmark(
            **sample_landmark_data,
            geom=WKTElement("POINT(-74.0060 40.7128)", srid=4326)
        )

        db_session.add(landmark)
        db_session.commit()

        assert landmark.id is not None
        assert landmark.name == sample_landmark_data["name"]
        assert landmark.landmark_type == sample_landmark_data["landmark_type"]

    def test_landmark_to_dict(self, sample_landmark_data):
        """Test landmark serialization."""
        landmark = Landmark(**sample_landmark_data)
        data = landmark.to_dict()

        assert data["name"] == sample_landmark_data["name"]
        assert data["landmark_type"] == sample_landmark_data["landmark_type"]
        assert "id" in data


class TestTaxIncentiveProgramModel:
    """Test TaxIncentiveProgram model."""

    def test_tax_incentive_program_creation(
        self, db_session, sample_tax_incentive_data
    ):
        """Test creating a tax incentive program."""
        program = TaxIncentiveProgram(**sample_tax_incentive_data)
        db_session.add(program)
        db_session.commit()

        assert program.id is not None
        assert program.program_code == sample_tax_incentive_data["program_code"]
        assert program.program_name == sample_tax_incentive_data["program_name"]

    def test_tax_incentive_program_to_dict(self, sample_tax_incentive_data):
        """Test tax incentive program serialization."""
        program = TaxIncentiveProgram(**sample_tax_incentive_data)
        data = program.to_dict()

        assert data["program_code"] == sample_tax_incentive_data["program_code"]
        assert data["program_name"] == sample_tax_incentive_data["program_name"]
        assert "id" in data


class TestPropertyTaxIncentiveModel:
    """Test PropertyTaxIncentive junction model."""

    def test_property_tax_incentive_creation(self, db_session):
        """Test creating property-tax incentive relationship."""
        # Create test property and program first
        property_obj = Property(
            address="123 Test St",
            lot_number="123-ABC",
            land_area_sf=2500.0,
            geom=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )
        db_session.add(property_obj)

        program = TaxIncentiveProgram(program_code="467-M", program_name="Test Program")
        db_session.add(program)
        db_session.commit()

        # Create relationship
        relationship = PropertyTaxIncentive(
            property_id=property_obj.id,
            tax_incentive_id=program.id,
            is_eligible=True,
            eligibility_reason="Test eligibility",
            estimated_abatement_value=100000.0,
        )
        db_session.add(relationship)
        db_session.commit()

        assert relationship.id is not None
        assert relationship.is_eligible is True
        assert relationship.estimated_abatement_value == 100000.0


class TestAirRightsModel:
    """Test AirRights model."""

    def test_air_rights_creation(self, db_session, sample_air_rights_data):
        """Test creating air rights record."""
        # Create test property first
        property_obj = Property(
            address="123 Test St",
            lot_number="123-ABC",
            land_area_sf=2500.0,
            geom=WKTElement("POINT(-74.0060 40.7128)", srid=4326),
        )
        db_session.add(property_obj)
        db_session.commit()

        air_rights = AirRights(property_id=property_obj.id, **sample_air_rights_data)
        db_session.add(air_rights)
        db_session.commit()

        assert air_rights.id is not None
        assert air_rights.property_id == property_obj.id
        assert air_rights.unused_far == sample_air_rights_data["unused_far"]

    def test_air_rights_to_dict(self, sample_air_rights_data):
        """Test air rights serialization."""
        air_rights = AirRights(**sample_air_rights_data)
        data = air_rights.to_dict()

        assert data["unused_far"] == sample_air_rights_data["unused_far"]
        assert data["transferable_far"] == sample_air_rights_data["transferable_far"]
        assert "id" in data
