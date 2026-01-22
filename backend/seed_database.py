#!/usr/bin/env python3
"""
Database seeding script for NYC Zoning Intelligence Platform.

This script populates the database with sample data for testing and development.
"""

import os
import uuid
from sqlalchemy import create_engine, text

# Database URL for Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/zoning_dev")

def create_sample_data():
    """Create sample data for testing."""

    # Create engine
    engine = create_engine(DATABASE_URL, echo=False)

    try:
        print("🌱 Seeding database with sample data...")

        with engine.connect() as conn:
            print("📍 Creating sample properties...")

            # Insert properties using individual SQL statements
            prop1_id = str(uuid.uuid4())
            prop2_id = str(uuid.uuid4())
            prop3_id = str(uuid.uuid4())
            prop4_id = str(uuid.uuid4())

            properties_data = [
                (prop1_id, "123 Broadway, Manhattan, NY 10007", "1", "17", "10007", 150000, 25000, "Office", "POINT(-74.0121 40.7074)"),
                (prop2_id, "456 Park Avenue, Manhattan, NY 10022", "45", "1234", "10022", 200000, 30000, "Residential", "POINT(-73.9708 40.7614)"),
                (prop3_id, "789 Flatbush Avenue, Brooklyn, NY 11217", "789", "567", "11217", 80000, 15000, "Mixed Use", "POINT(-73.9794 40.6872)"),
                (prop4_id, "321 Queens Boulevard, Queens, NY 11375", "321", "890", "11375", 120000, 20000, "Commercial", "POINT(-73.8448 40.7198)")
            ]

            properties_sql = """
            INSERT INTO properties (id, address, lot_number, block_number, zip_code, building_area_sf, land_area_sf, current_use, geom)
            VALUES (:id, :address, :lot_number, :block_number, :zip_code, :building_area_sf, :land_area_sf, :current_use, ST_GeomFromText(:geom, 4326))
            """

            for prop_data in properties_data:
                prop_dict = {
                    'id': prop_data[0], 'address': prop_data[1], 'lot_number': prop_data[2],
                    'block_number': prop_data[3], 'zip_code': prop_data[4], 'building_area_sf': prop_data[5],
                    'land_area_sf': prop_data[6], 'current_use': prop_data[7], 'geom': prop_data[8]
                }
                conn.execute(text(properties_sql), prop_dict)
            conn.commit()

            # Store property IDs for later use
            properties_data = [
                {"id": prop1_id, "address": "123 Broadway, Manhattan, NY 10007"},
                {"id": prop2_id, "address": "456 Park Avenue, Manhattan, NY 10022"},
                {"id": prop3_id, "address": "789 Flatbush Avenue, Brooklyn, NY 11217"},
                {"id": prop4_id, "address": "321 Queens Boulevard, Queens, NY 11375"}
            ]

            print("🏛️ Creating sample zoning districts...")

            # Insert zoning districts using individual SQL statements
            zone1_id = str(uuid.uuid4())
            zone2_id = str(uuid.uuid4())
            zone3_id = str(uuid.uuid4())

            zoning_data = [
                (zone1_id, "C6-4", "Commercial District - Medium Density", 6.0, 8.0, 200,
                 '{"front": 0, "rear": 15, "side": 5}', "C",
                 "MULTIPOLYGON(((-74.0121 40.7074, -74.0125 40.7074, -74.0125 40.7078, -74.0121 40.7078, -74.0121 40.7074)))"),
                (zone2_id, "R10", "Residential District - High Density", 10.0, 12.0, 300,
                 '{"front": 0, "rear": 20, "side": 8}', "R",
                 "MULTIPOLYGON(((-73.9708 40.7614, -73.9712 40.7614, -73.9712 40.7618, -73.9708 40.7618, -73.9708 40.7614)))"),
                (zone3_id, "M1-1", "Manufacturing District - Light", 2.0, 3.0, 85,
                 '{"front": 0, "rear": 10, "side": 0}', "M",
                 "MULTIPOLYGON(((-73.9794 40.6872, -73.9798 40.6872, -73.9798 40.6876, -73.9794 40.6876, -73.9794 40.6872)))")
            ]

            zoning_sql = """
            INSERT INTO zoning_districts (id, district_code, district_name, far_base, far_with_bonus, max_height_ft, setback_requirements, building_class, geom)
            VALUES (:id, :district_code, :district_name, :far_base, :far_with_bonus, :max_height_ft, :setback_requirements, :building_class, ST_GeomFromText(:geom, 4326))
            """

            for zone_data in zoning_data:
                zone_dict = {
                    'id': zone_data[0], 'district_code': zone_data[1], 'district_name': zone_data[2],
                    'far_base': zone_data[3], 'far_with_bonus': zone_data[4], 'max_height_ft': zone_data[5],
                    'setback_requirements': zone_data[6], 'building_class': zone_data[7], 'geom': zone_data[8]
                }
                conn.execute(text(zoning_sql), zone_dict)
            conn.commit()

            # Store zoning district IDs for later use
            zoning_data = [
                {"id": zone1_id, "code": "C6-4"},
                {"id": zone2_id, "code": "R10"},
                {"id": zone3_id, "code": "M1-1"}
            ]

            print("🏛️ Creating sample landmarks...")

            # Insert landmarks using individual SQL statements
            landmarks_data = [
                (str(uuid.uuid4()), "Empire State Building", "cultural", "Iconic Art Deco skyscraper and cultural landmark", "POINT(-73.9857 40.7484)"),
                (str(uuid.uuid4()), "Brooklyn Bridge", "transportation", "Historic suspension bridge connecting Manhattan and Brooklyn", "POINT(-73.9969 40.7061)"),
                (str(uuid.uuid4()), "Central Park", "natural", "843-acre urban park in Manhattan", "POINT(-73.9654 40.7829)"),
                (str(uuid.uuid4()), "One World Trade Center", "historic", "Memorial and observation tower at the World Trade Center site", "POINT(-74.0134 40.7127)")
            ]

            landmarks_sql = """
            INSERT INTO landmarks (id, name, landmark_type, description, geom)
            VALUES (:id, :name, :landmark_type, :description, ST_GeomFromText(:geom, 4326))
            """

            for landmark_data in landmarks_data:
                landmark_dict = {
                    'id': landmark_data[0], 'name': landmark_data[1], 'landmark_type': landmark_data[2],
                    'description': landmark_data[3], 'geom': landmark_data[4]
                }
                conn.execute(text(landmarks_sql), landmark_dict)
            conn.commit()

            print("💰 Creating sample tax incentive programs...")

            # Insert tax incentive programs using individual SQL statements
            prog1_id = str(uuid.uuid4())
            prog2_id = str(uuid.uuid4())
            prog3_id = str(uuid.uuid4())

            tax_programs_data = [
                (prog1_id, "ICAP", "Industrial and Commercial Abatement Program",
                 "Tax abatement for industrial and commercial properties",
                 '["M1-1", "M2-1", "M3-1"]', 5, False, 10),
                (prog2_id, "467-M", "Historic Preservation Tax Credit",
                 "Tax credits for historic building preservation and renovation",
                 '["R6", "R7", "R8", "R9", "R10"]', 30, False, 12),
                (prog3_id, "421-A", "Residential Tax Abatement",
                 "Tax abatement for residential property development",
                 '["R6", "R7", "R8", "R9", "R10"]', None, True, 25)
            ]

            tax_programs_sql = """
            INSERT INTO tax_incentive_programs (id, program_code, program_name, description, eligible_zoning_districts, min_building_age, requires_residential, tax_abatement_years)
            VALUES (:id, :program_code, :program_name, :description, :eligible_zoning_districts, :min_building_age, :requires_residential, :tax_abatement_years)
            """

            for program_data in tax_programs_data:
                program_dict = {
                    'id': program_data[0], 'program_code': program_data[1], 'program_name': program_data[2],
                    'description': program_data[3], 'eligible_zoning_districts': program_data[4],
                    'min_building_age': program_data[5], 'requires_residential': program_data[6],
                    'tax_abatement_years': program_data[7]
                }
                conn.execute(text(tax_programs_sql), program_dict)
            conn.commit()

            # Store tax program IDs for later use
            tax_programs_data = [
                {"id": prog1_id, "code": "ICAP"},
                {"id": prog2_id, "code": "467-M"},
                {"id": prog3_id, "code": "421-A"}
            ]

            print("🛩️ Creating sample air rights data...")

            # Insert air rights using individual SQL statements
            air_rights_data = [
                (str(uuid.uuid4()), prop1_id, 2.5, 1.8, 45.50, f'["{prop2_id}"]'),
                (str(uuid.uuid4()), prop2_id, 4.2, 3.1, 78.25, f'["{prop1_id}"]')
            ]

            air_rights_sql = """
            INSERT INTO air_rights (id, property_id, unused_far, transferable_far, tdr_price_per_sf, adjacent_property_ids)
            VALUES (:id, :property_id, :unused_far, :transferable_far, :tdr_price_per_sf, :adjacent_property_ids)
            """

            for air_right_data in air_rights_data:
                air_right_dict = {
                    'id': air_right_data[0], 'property_id': air_right_data[1], 'unused_far': air_right_data[2],
                    'transferable_far': air_right_data[3], 'tdr_price_per_sf': air_right_data[4],
                    'adjacent_property_ids': air_right_data[5]
                }
                conn.execute(text(air_rights_sql), air_right_dict)
            conn.commit()

            # Link properties to zoning districts
            print("🔗 Linking properties to zoning districts...")

            property_zoning_data = [
                (str(uuid.uuid4()), prop1_id, zone1_id, 100),
                (str(uuid.uuid4()), prop2_id, zone2_id, 100),
                (str(uuid.uuid4()), prop3_id, zone3_id, 100),
                (str(uuid.uuid4()), prop4_id, zone1_id, 100)
            ]

            property_zoning_sql = """
            INSERT INTO property_zoning (id, property_id, zoning_district_id, percent_in_district)
            VALUES (:id, :property_id, :zoning_district_id, :percent_in_district)
            """

            for pz_data in property_zoning_data:
                pz_dict = {
                    'id': pz_data[0], 'property_id': pz_data[1], 'zoning_district_id': pz_data[2],
                    'percent_in_district': pz_data[3]
                }
                conn.execute(text(property_zoning_sql), pz_dict)
            conn.commit()

            # Link properties to tax incentives
            print("💰 Linking properties to tax incentives...")

            property_tax_data = [
                (str(uuid.uuid4()), prop1_id, prog1_id, True, "Located in manufacturing district", 150000),
                (str(uuid.uuid4()), prop2_id, prog2_id, True, "Historic building preservation", 200000),
                (str(uuid.uuid4()), prop3_id, prog3_id, False, "Not a residential property", 0)
            ]

            property_tax_sql = """
            INSERT INTO property_tax_incentives (id, property_id, program_id, is_eligible, eligibility_reason, estimated_abatement_value)
            VALUES (:id, :property_id, :program_id, :is_eligible, :eligibility_reason, :estimated_abatement_value)
            """

            for pt_data in property_tax_data:
                pt_dict = {
                    'id': pt_data[0], 'property_id': pt_data[1], 'program_id': pt_data[2],
                    'is_eligible': pt_data[3], 'eligibility_reason': pt_data[4],
                    'estimated_abatement_value': pt_data[5]
                }
                conn.execute(text(property_tax_sql), pt_dict)
            conn.commit()

        print("✅ Database seeding completed successfully!")
        print("   📍 Created 4 sample properties")
        print("   🏛️ Created 3 zoning districts")
        print("   🏛️ Created 4 landmarks")
        print("   💰 Created 3 tax incentive programs")
        print("   🛩️ Created 2 air rights records")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise

if __name__ == "__main__":
    create_sample_data()