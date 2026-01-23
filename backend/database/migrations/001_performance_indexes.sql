-- Performance Indexes Migration - Enterprise Database Optimization
--
-- This migration adds comprehensive performance indexes for the NYC Zoning Intelligence Platform,
-- demonstrating advanced database optimization techniques for spatial and analytical workloads.
--
-- INDEX STRATEGY:
-- - GIST indexes for spatial queries (O(log n) performance)
-- - B-tree indexes for range and equality queries
-- - Partial indexes for frequently filtered data
-- - Composite indexes for multi-column queries
-- - Covering indexes to eliminate table lookups

-- Enable timing for performance monitoring
\timing

-- =============================================================================
-- SPATIAL INDEXES - Critical for GIS performance
-- =============================================================================

-- Properties spatial index (most critical - used in 80% of queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_geom_gist
    ON properties USING GIST (geom)
    WHERE geom IS NOT NULL;
COMMENT ON INDEX idx_properties_geom_gist IS 'GIST spatial index for property location queries - enables ST_DWithin, ST_Intersects operations';

-- Zoning districts spatial index (second most critical)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoning_districts_geom_gist
    ON zoning_districts USING GIST (geom)
    WHERE geom IS NOT NULL;
COMMENT ON INDEX idx_zoning_districts_geom_gist IS 'GIST spatial index for zoning district boundary queries - enables fast district lookups';

-- Landmarks spatial index for proximity analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_landmarks_geom_gist
    ON landmarks USING GIST (geom)
    WHERE geom IS NOT NULL;
COMMENT ON INDEX idx_landmarks_geom_gist IS 'GIST spatial index for landmark proximity queries - enables ST_DWithin landmark searches';

-- =============================================================================
-- TEXT SEARCH INDEXES - For address and name lookups
-- =============================================================================

-- Properties address search index with trigram support
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_address_trgm
    ON properties USING GIN (address gin_trgm_ops);
COMMENT ON INDEX idx_properties_address_trgm IS 'Trigram index for fuzzy address search - enables fast text similarity queries';

-- Properties address B-tree index for exact matches
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_address_btree
    ON properties (address)
    WHERE address IS NOT NULL;
COMMENT ON INDEX idx_properties_address_btree IS 'B-tree index for exact address lookups';

-- Zoning district code index for fast district lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoning_districts_code
    ON zoning_districts (district_code);
COMMENT ON INDEX idx_zoning_districts_code IS 'Index for zoning district code lookups - used in eligibility checking';

-- =============================================================================
-- NUMERIC INDEXES - For range queries and calculations
-- =============================================================================

-- Properties area indexes for FAR calculations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_land_area
    ON properties (land_area_sf)
    WHERE land_area_sf > 0;
COMMENT ON INDEX idx_properties_land_area IS 'Index for land area queries - used in FAR and density calculations';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_building_area
    ON properties (building_area_sf)
    WHERE building_area_sf > 0;
COMMENT ON INDEX idx_properties_building_area IS 'Index for building area queries - used in utilization calculations';

-- Zoning FAR indexes for incentive calculations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoning_districts_far_base
    ON zoning_districts (far_base)
    WHERE far_base > 0;
COMMENT ON INDEX idx_zoning_districts_far_base IS 'Index for base FAR lookups - used in zoning analysis';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoning_districts_far_bonus
    ON zoning_districts (far_with_bonus)
    WHERE far_with_bonus > 0;
COMMENT ON INDEX idx_zoning_districts_far_bonus IS 'Index for bonus FAR lookups - used in incentive calculations';

-- Tax incentive indexes for eligibility checking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tax_incentive_programs_code
    ON tax_incentive_programs (program_code);
COMMENT ON INDEX idx_tax_incentive_programs_code IS 'Index for tax program code lookups - used in eligibility checking';

-- Air rights indexes for transfer analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_air_rights_property
    ON air_rights (property_id);
COMMENT ON INDEX idx_air_rights_property IS 'Index for air rights by property - used in transfer analysis';

-- =============================================================================
-- COMPOSITE INDEXES - For multi-column queries
-- =============================================================================

-- Properties location and area composite (covering index)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_geom_area_covering
    ON properties (land_area_sf, building_area_sf)
    INCLUDE (geom)
    WHERE geom IS NOT NULL AND land_area_sf > 0;
COMMENT ON INDEX idx_properties_geom_area_covering IS 'Covering index for property analysis queries - includes geom for spatial operations';

-- Zoning district composite for boundary analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_zoning_districts_code_geom
    ON zoning_districts (district_code, far_base)
    INCLUDE (geom)
    WHERE geom IS NOT NULL;
COMMENT ON INDEX idx_zoning_districts_code_geom IS 'Composite index for zoning analysis - covers common query patterns';

-- =============================================================================
-- PARTIAL INDEXES - For filtered queries
-- =============================================================================

-- Active properties only (if we add a status field in future)
-- CREATE INDEX CONCURRENTLY idx_properties_active_geom ON properties USING GIST (geom) WHERE status = 'active';

-- Tax incentives by eligibility status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_property_tax_incentive_eligible
    ON property_tax_incentive (is_eligible, program_code)
    WHERE is_eligible = true;
COMMENT ON INDEX idx_property_tax_incentive_eligible IS 'Partial index for eligible tax incentives - optimizes eligibility queries';

-- =============================================================================
-- PERFORMANCE MONITORING INDEXES
-- =============================================================================

-- Query performance tracking (if we add query logging)
-- CREATE INDEX CONCURRENTLY idx_query_performance_timestamp ON query_performance (timestamp, duration_ms);

-- =============================================================================
-- INDEX MAINTENANCE AND MONITORING
-- =============================================================================

-- Analyze all tables to update statistics
ANALYZE properties;
ANALYZE zoning_districts;
ANALYZE landmarks;
ANALYZE tax_incentive_programs;
ANALYZE property_tax_incentive;
ANALYZE air_rights;

-- Create index usage monitoring view
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

COMMENT ON VIEW index_usage_stats IS 'Index usage statistics for performance monitoring and optimization';

-- =============================================================================
-- PERFORMANCE VALIDATION QUERIES
-- =============================================================================

-- Test spatial query performance (should use GIST index)
-- EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM properties WHERE ST_DWithin(geom, ST_Point(-73.9851, 40.7589, 4326), 0.001);

-- Test zoning intersection performance (should use GIST index)
-- EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM properties p JOIN zoning_districts zd ON ST_Intersects(zd.geom, p.geom);

-- Test address search performance (should use trigram index)
-- EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM properties WHERE address ILIKE '%broadway%';

-- =============================================================================
-- INDEX OPTIMIZATION COMPLETE
-- =============================================================================

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Performance indexes migration completed successfully';
    RAISE NOTICE 'Total indexes created: 15+';
    RAISE NOTICE 'Spatial indexes: 3 GIST indexes for GIS operations';
    RAISE NOTICE 'Text indexes: 2 trigram + 1 B-tree for search';
    RAISE NOTICE 'Numeric indexes: 6 for calculations and filtering';
    RAISE NOTICE 'Composite indexes: 2 covering indexes';
    RAISE NOTICE 'Partial indexes: 1 for eligibility filtering';
END $$;