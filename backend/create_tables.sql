-- Create tables for NYC Zoning Intelligence Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Properties table
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address VARCHAR(500) NOT NULL,
    lot_number VARCHAR(10),
    block_number VARCHAR(10),
    zip_code VARCHAR(10),
    building_area_sf FLOAT,
    land_area_sf FLOAT NOT NULL,
    current_use VARCHAR(100),
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for properties
CREATE INDEX idx_properties_id ON properties(id);
CREATE INDEX idx_properties_address ON properties(address);
CREATE INDEX idx_properties_geom ON properties USING GIST(geom);

-- Zoning districts table
CREATE TABLE zoning_districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    district_code VARCHAR(20) UNIQUE NOT NULL,
    district_name VARCHAR(200),
    far_base FLOAT NOT NULL,
    far_with_bonus FLOAT NOT NULL,
    max_height_ft FLOAT,
    setback_requirements JSONB,
    building_class VARCHAR(10),
    geom GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for zoning districts
CREATE INDEX idx_zoning_districts_id ON zoning_districts(id);
CREATE INDEX idx_zoning_districts_district_code ON zoning_districts(district_code);
CREATE INDEX idx_zoning_districts_geom ON zoning_districts USING GIST(geom);

-- Property zoning junction table
CREATE TABLE property_zoning (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    zoning_district_id UUID NOT NULL REFERENCES zoning_districts(id) ON DELETE CASCADE,
    percent_in_district FLOAT NOT NULL
);

-- Create indexes for property zoning
CREATE INDEX idx_property_zoning_property_id ON property_zoning(property_id);
CREATE INDEX idx_property_zoning_zoning_district_id ON property_zoning(zoning_district_id);

-- Landmarks table
CREATE TABLE landmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    landmark_type VARCHAR(50) NOT NULL,
    description TEXT,
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for landmarks
CREATE INDEX idx_landmarks_id ON landmarks(id);
CREATE INDEX idx_landmarks_name ON landmarks(name);
CREATE INDEX idx_landmarks_landmark_type ON landmarks(landmark_type);
CREATE INDEX idx_landmarks_geom ON landmarks USING GIST(geom);

-- Tax incentive programs table
CREATE TABLE tax_incentive_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program_code VARCHAR(20) UNIQUE NOT NULL,
    program_name VARCHAR(200) NOT NULL,
    description TEXT,
    eligible_zoning_districts JSONB,
    min_building_age INTEGER,
    requires_residential BOOLEAN DEFAULT FALSE,
    tax_abatement_years INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for tax incentive programs
CREATE INDEX idx_tax_incentive_programs_id ON tax_incentive_programs(id);
CREATE INDEX idx_tax_incentive_programs_program_code ON tax_incentive_programs(program_code);

-- Property tax incentives junction table
CREATE TABLE property_tax_incentives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES tax_incentive_programs(id) ON DELETE CASCADE,
    is_eligible BOOLEAN,
    eligibility_reason TEXT,
    estimated_abatement_value FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for property tax incentives
CREATE INDEX idx_property_tax_incentives_program_id ON property_tax_incentives(program_id);
CREATE INDEX idx_property_tax_incentives_property_id ON property_tax_incentives(property_id);

-- Air rights table
CREATE TABLE air_rights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID UNIQUE NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    unused_far FLOAT DEFAULT 0.0,
    transferable_far FLOAT DEFAULT 0.0,
    tdr_price_per_sf FLOAT,
    adjacent_property_ids JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for air rights
CREATE INDEX idx_air_rights_id ON air_rights(id);
CREATE INDEX idx_air_rights_property_id ON air_rights(property_id);

-- Create alembic version table
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Insert initial alembic version
INSERT INTO alembic_version (version_num) VALUES ('0001_initial');