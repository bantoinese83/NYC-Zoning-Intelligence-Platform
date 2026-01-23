-- NYC Zoning Platform - Final Building Footprints Import
-- Complete import of all building footprint data

-- ==================================================
-- STEP 1: CREATE TEMPORARY TABLE
-- ==================================================

DROP TABLE IF EXISTS building_footprints_raw;
CREATE TEMP TABLE building_footprints_raw (
    the_geom TEXT,
    name TEXT,
    bin TEXT,
    doitt_id TEXT,
    shape_area TEXT,
    base_bbl TEXT,
    objectid TEXT,
    construction_year TEXT,
    feature_code TEXT,
    geometry_source TEXT,
    ground_elevation TEXT,
    height_roof TEXT,
    last_edited_date TEXT,
    last_status_type TEXT,
    map_pluto_bbl TEXT,
    length TEXT
);

-- ==================================================
-- STEP 2: IMPORT CSV DATA
-- ==================================================

\COPY building_footprints_raw FROM '/tmp/BUILDING-20260122.csv' WITH CSV HEADER;

-- ==================================================
-- STEP 3: IMPORT IN BATCHES TO AVOID ISSUES
-- ==================================================

-- Batch 1: Import buildings with valid geometry (first 100,000)
INSERT INTO building_footprints (
    bin, doitt_id, base_bbl, construction_year, height_roof,
    ground_elevation, shape_area, feature_code, geometry_source,
    last_status_type, geom, created_at
)
SELECT
    bin,
    doitt_id,
    base_bbl,
    CASE
        WHEN construction_year ~ '^[0-9]+$'
        THEN construction_year::INTEGER
        WHEN construction_year ~ '^[0-9,]+$'
        THEN REPLACE(construction_year, ',', '')::INTEGER
        ELSE NULL
    END,
    CASE WHEN height_roof ~ '^[0-9.]+$' THEN height_roof::DECIMAL ELSE NULL END,
    CASE WHEN ground_elevation ~ '^[0-9.]+$' THEN ground_elevation::DECIMAL ELSE NULL END,
    CASE WHEN shape_area ~ '^[0-9.]+$' THEN shape_area::DECIMAL ELSE NULL END,
    feature_code,
    geometry_source,
    last_status_type,
    ST_GeomFromText(the_geom, 4326),
    NOW()
FROM building_footprints_raw
WHERE bin IS NOT NULL AND bin != ''
  AND the_geom IS NOT NULL AND the_geom != ''
  AND the_geom LIKE 'MULTIPOLYGON%'
ORDER BY bin
LIMIT 100000;

-- Batch 2: Import remaining buildings (next 200,000)
INSERT INTO building_footprints (
    bin, doitt_id, base_bbl, construction_year, height_roof,
    ground_elevation, shape_area, feature_code, geometry_source,
    last_status_type, geom, created_at
)
SELECT
    bin,
    doitt_id,
    base_bbl,
    CASE
        WHEN construction_year ~ '^[0-9]+$'
        THEN construction_year::INTEGER
        WHEN construction_year ~ '^[0-9,]+$'
        THEN REPLACE(construction_year, ',', '')::INTEGER
        ELSE NULL
    END,
    CASE WHEN height_roof ~ '^[0-9.]+$' THEN height_roof::DECIMAL ELSE NULL END,
    CASE WHEN ground_elevation ~ '^[0-9.]+$' THEN ground_elevation::DECIMAL ELSE NULL END,
    CASE WHEN shape_area ~ '^[0-9.]+$' THEN shape_area::DECIMAL ELSE NULL END,
    feature_code,
    geometry_source,
    last_status_type,
    ST_GeomFromText(the_geom, 4326),
    NOW()
FROM building_footprints_raw
WHERE bin IS NOT NULL AND bin != ''
  AND the_geom IS NOT NULL AND the_geom != ''
  AND the_geom LIKE 'MULTIPOLYGON%'
  AND NOT EXISTS (SELECT 1 FROM building_footprints bf WHERE bf.bin = building_footprints_raw.bin)
ORDER BY bin
LIMIT 200000;

-- ==================================================
-- STEP 4: CLEAN UP
-- ==================================================

DROP TABLE building_footprints_raw;

-- ==================================================
-- STEP 5: FINAL VERIFICATION
-- ==================================================

SELECT
    'Building Footprints' as dataset,
    COUNT(*) as total_records,
    COUNT(CASE WHEN geom IS NOT NULL THEN 1 END) as with_valid_geometry,
    COUNT(CASE WHEN construction_year IS NOT NULL THEN 1 END) as with_construction_year,
    COUNT(CASE WHEN height_roof IS NOT NULL THEN 1 END) as with_height_data,
    ROUND(AVG(CASE WHEN construction_year IS NOT NULL THEN construction_year END), 0) as avg_construction_year,
    ROUND(AVG(CASE WHEN height_roof IS NOT NULL THEN height_roof END), 2) as avg_height_feet,
    ROUND(MIN(CASE WHEN construction_year IS NOT NULL THEN construction_year END), 0) as oldest_building,
    ROUND(MAX(CASE WHEN construction_year IS NOT NULL THEN construction_year END), 0) as newest_building,
    'NYC building polygons with heights & construction data' as notes
FROM building_footprints;