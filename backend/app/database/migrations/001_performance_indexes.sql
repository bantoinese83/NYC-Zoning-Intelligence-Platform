-- Performance optimization indexes for zoning platform
-- Run this migration to add performance indexes to the database

-- Properties table indexes
CREATE INDEX IF NOT EXISTS idx_properties_address_gin ON properties USING gin (to_tsvector('english', address));
CREATE INDEX IF NOT EXISTS idx_properties_zip_code ON properties (zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_current_use ON properties (current_use);
CREATE INDEX IF NOT EXISTS idx_properties_building_area ON properties (building_area_sf);
CREATE INDEX IF NOT EXISTS idx_properties_land_area ON properties (land_area_sf);
CREATE INDEX IF NOT EXISTS idx_properties_geom_gist ON properties USING gist (geom);

-- Zoning districts spatial index (should already exist but ensuring)
CREATE INDEX IF NOT EXISTS idx_zoning_districts_geom_gist ON zoning_districts USING gist (geom);

-- Property zoning junction table indexes
CREATE INDEX IF NOT EXISTS idx_property_zoning_property_id ON property_zoning (property_id);
CREATE INDEX IF NOT EXISTS idx_property_zoning_district_id ON property_zoning (zoning_district_id);
CREATE INDEX IF NOT EXISTS idx_property_zoning_percent ON property_zoning (percent_in_district);

-- Tax incentives indexes
CREATE INDEX IF NOT EXISTS idx_property_tax_incentive_property_id ON property_tax_incentive (property_id);
CREATE INDEX IF NOT EXISTS idx_property_tax_incentive_program_id ON property_tax_incentive (tax_incentive_id);
CREATE INDEX IF NOT EXISTS idx_property_tax_incentive_eligible ON property_tax_incentive (is_eligible);

-- Landmarks spatial index
CREATE INDEX IF NOT EXISTS idx_landmarks_geom_gist ON landmarks USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_landmarks_type ON landmarks (landmark_type);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_properties_address_zip ON properties (address, zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_area_combined ON properties (building_area_sf, land_area_sf);

-- Partial indexes for frequently filtered data
CREATE INDEX IF NOT EXISTS idx_properties_with_building_area ON properties (building_area_sf) WHERE building_area_sf IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_with_coordinates ON properties (latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;