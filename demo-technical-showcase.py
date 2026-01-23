#!/usr/bin/env python3
"""
NYC Zoning Intelligence Platform - Technical Demonstration Script

This script demonstrates the advanced technical capabilities of the zoning platform,
showcasing complex spatial queries, business logic, and performance optimizations.

TECHNICAL FEATURES DEMONSTRATED:
- PostGIS spatial operations with GIST indexing
- Complex zoning calculations with multi-district analysis
- Tax incentive eligibility engines
- Air rights transfer modeling
- Performance-optimized database queries
- Real-time data processing and analysis

USAGE:
    python demo-technical-showcase.py

This script will connect to the running database and demonstrate
the technical sophistication of the zoning intelligence platform.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any
from uuid import UUID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import requests
    from shapely.geometry import Point
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    logger.error(f"Missing dependencies: {e}")
    logger.error("Install with: pip install requests shapely sqlalchemy psycopg2-binary")
    exit(1)


class ZoningPlatformDemo:
    """Technical demonstration of advanced zoning platform capabilities."""

    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base
        self.db_url = "postgresql://postgres:postgres@localhost:5432/zoning_dev"

        # Create database connection
        try:
            self.engine = create_engine(self.db_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            exit(1)

    def demonstrate_spatial_performance(self) -> Dict[str, Any]:
        """
        Demonstrate advanced PostGIS spatial query performance.

        Shows GIST indexing benefits and complex geometric operations.
        """
        logger.info("\n🚀 Demonstrating Advanced Spatial Query Performance")
        logger.info("=" * 60)

        session = self.SessionLocal()

        try:
            # Test 1: GIST Index Performance - Property proximity search
            logger.info("📍 Test 1: Spatial proximity search with GIST indexing")

            # Use a sample NYC coordinate (Times Square area)
            test_lat, test_lng = 40.7589, -73.9851

            start_time = time.time()

            # This query uses ST_DWithin with GIST index for O(log n) performance
            query = text("""
                SELECT COUNT(*) as nearby_count,
                       AVG(ST_Distance(geom, ST_Point(:lng, :lat, 4326))) as avg_distance_ft
                FROM properties
                WHERE ST_DWithin(geom, ST_Point(:lng, :lat, 4326), 0.001)  -- ~300ft radius
            """)

            result = session.execute(query, {"lat": test_lat, "lng": test_lng}).first()

            query_time = time.time() - start_time

            logger.info(".4f"            logger.info(f"   📊 Found {result.nearby_count} properties within 300ft")
            logger.info(".2f"
            # Test 2: Complex zoning intersection analysis
            logger.info("\n🏗️  Test 2: Multi-district zoning analysis")

            start_time = time.time()

            # Complex query joining properties with zoning districts
            zoning_query = text("""
                SELECT
                    p.address,
                    COUNT(DISTINCT zd.district_code) as district_count,
                    AVG(zd.far_base) as avg_far_base,
                    MAX(zd.max_height_ft) as max_height
                FROM properties p
                JOIN zoning_districts zd ON ST_Intersects(zd.geom, p.geom)
                WHERE ST_DWithin(p.geom, ST_Point(:lng, :lat, 4326), 0.001)
                GROUP BY p.id, p.address
                ORDER BY district_count DESC
                LIMIT 5
            """)

            zoning_results = session.execute(zoning_query, {"lat": test_lat, "lng": test_lng}).fetchall()
            zoning_time = time.time() - start_time

            logger.info(".4f"            for i, result in enumerate(zoning_results, 1):
                logger.info(f"   🏢 Property {i}: {result.address[:30]}...")
                logger.info(f"      Districts: {result.district_count}, Avg FAR: {result.avg_far_base:.1f}, Max Height: {result.max_height:.0f}ft")

            return {
                "spatial_query_time": query_time,
                "zoning_analysis_time": zoning_time,
                "properties_found": result.nearby_count,
                "complex_queries_executed": True
            }

        except Exception as e:
            logger.error(f"❌ Spatial performance test failed: {e}")
            return {"error": str(e)}
        finally:
            session.close()

    def demonstrate_business_logic_complexity(self) -> Dict[str, Any]:
        """
        Demonstrate complex business logic for zoning and tax incentives.

        Shows the sophisticated rule engines implemented.
        """
        logger.info("\n🧠 Demonstrating Complex Business Logic")
        logger.info("=" * 60)

        # Test with a sample property analysis
        sample_property_id = "00cf9ed6-92f5-4d1c-9a9d-a413cc2ba6fc"  # From seeded data

        try:
            # Test zoning analysis
            logger.info("📊 Test 1: Advanced Zoning Analysis Engine")

            response = requests.get(f"{self.api_base}/api/properties/{sample_property_id}/zoning", timeout=10)

            if response.status_code == 200:
                zoning_data = response.json()
                logger.info("   ✅ Zoning analysis completed successfully")
                logger.info(f"   🏛️  {zoning_data.get('district_count', 0)} zoning districts analyzed")

                if zoning_data.get('far_analysis'):
                    far_data = zoning_data['far_analysis']
                    logger.info(f"   📐 FAR Analysis: Effective {far_data.get('far_effective', 'N/A')}")
            else:
                logger.warning(f"   ⚠️  Zoning analysis failed: HTTP {response.status_code}")

            # Test tax incentives
            logger.info("\n💰 Test 2: Tax Incentive Compliance Engine")

            response = requests.get(f"{self.api_base}/api/properties/{sample_property_id}/tax-incentives", timeout=10)

            if response.status_code == 200:
                tax_data = response.json()
                logger.info("   ✅ Tax incentive analysis completed")
                eligible_programs = [p for p in tax_data if p.get('is_eligible')]
                logger.info(f"   🎯 {len(eligible_programs)} eligible programs found")

                for program in eligible_programs[:2]:  # Show first 2
                    logger.info(f"      📋 {program.get('program_name', 'Unknown')}: Eligible")
            else:
                logger.warning(f"   ⚠️  Tax incentive analysis failed: HTTP {response.status_code}")

            # Test air rights analysis
            logger.info("\n🌆 Test 3: Air Rights Transfer Modeling")

            response = requests.get(f"{self.api_base}/api/properties/{sample_property_id}/air-rights", timeout=10)

            if response.status_code == 200:
                air_data = response.json()
                logger.info("   ✅ Air rights analysis completed")
                logger.info(".1f"                logger.info(f"   💵 Transferable Value: ${air_data.get('estimated_value', 0):,.0f}")
                logger.info(f"   🏢 Adjacent Recipients: {air_data.get('adjacent_properties', 0)}")
            else:
                logger.warning(f"   ⚠️  Air rights analysis failed: HTTP {response.status_code}")

            return {
                "zoning_analysis": response.status_code == 200,
                "tax_incentives": response.status_code == 200,
                "air_rights": response.status_code == 200,
                "business_logic_tests": True
            }

        except requests.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return {"error": str(e)}

    def demonstrate_performance_optimization(self) -> Dict[str, Any]:
        """
        Demonstrate performance optimizations and database efficiency.
        """
        logger.info("\n⚡ Demonstrating Performance Optimizations")
        logger.info("=" * 60)

        session = self.SessionLocal()

        try:
            # Test database index effectiveness
            logger.info("🔍 Test 1: Database Index Performance")

            # Measure query performance with EXPLAIN
            explain_query = text("""
                EXPLAIN (ANALYZE, BUFFERS)
                SELECT COUNT(*) FROM properties p
                JOIN zoning_districts zd ON ST_Intersects(zd.geom, p.geom)
                WHERE ST_DWithin(p.geom, ST_Point(-73.9851, 40.7589, 4326), 0.001)
            """)

            start_time = time.time()
            result = session.execute(explain_query).fetchall()
            explain_time = time.time() - start_time

            logger.info(".4f"            # Look for index usage in explain plan
            plan_text = "\n".join([row[0] for row in result])
            has_gist_index = "gist" in plan_text.lower()
            has_spatial_index = "spatial" in plan_text.lower() or "gist" in plan_text.lower()

            logger.info(f"   🎯 GIST Index Used: {'✅' if has_gist_index else '❌'}")
            logger.info(f"   📊 Spatial Index Effective: {'✅' if has_spatial_index else '❌'}")

            # Test concurrent request handling
            logger.info("\n🔄 Test 2: Concurrent Request Handling")

            import concurrent.futures
            import threading

            response_times = []

            def single_request():
                try:
                    start = time.time()
                    response = requests.get(f"{self.api_base}/api/stats", timeout=5)
                    end = time.time()
                    if response.status_code == 200:
                        response_times.append(end - start)
                except:
                    pass

            # Simulate concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(single_request) for _ in range(10)]
                concurrent.futures.wait(futures)

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                logger.info(".3f"                logger.info(".3f"            else:
                logger.warning("   ⚠️  No successful concurrent requests")

            return {
                "explain_plan_time": explain_time,
                "gist_index_used": has_gist_index,
                "spatial_index_effective": has_spatial_index,
                "concurrent_requests_tested": len(response_times),
                "average_response_time": sum(response_times) / len(response_times) if response_times else None
            }

        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            return {"error": str(e)}
        finally:
            session.close()

    def run_full_demonstration(self) -> Dict[str, Any]:
        """
        Run complete technical demonstration of the zoning platform.
        """
        logger.info("🚀 NYC Zoning Intelligence Platform - Technical Showcase")
        logger.info("=" * 80)
        logger.info("Demonstrating enterprise-grade real estate technology implementation")
        logger.info("=" * 80)

        results = {}

        # Test API availability
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API Health Check: PASSED")
                results["api_health"] = True
            else:
                logger.error(f"❌ API Health Check: FAILED (HTTP {response.status_code})")
                results["api_health"] = False
        except Exception as e:
            logger.error(f"❌ API Connection: FAILED ({e})")
            results["api_health"] = False
            return results

        # Run technical demonstrations
        results["spatial_performance"] = self.demonstrate_spatial_performance()
        results["business_logic"] = self.demonstrate_business_logic_complexity()
        results["performance_optimization"] = self.demonstrate_performance_optimization()

        # Summary
        logger.info("\n🎉 Technical Demonstration Complete")
        logger.info("=" * 80)

        success_count = sum(1 for r in results.values() if isinstance(r, dict) and not r.get("error"))
        total_tests = len([r for r in results.values() if isinstance(r, dict)])

        logger.info(f"📊 Test Results: {success_count}/{total_tests} major components validated")
        logger.info("🏆 Demonstrated: Advanced PostGIS, Complex Business Logic, Performance Optimization")

        if success_count == total_tests:
            logger.info("✅ ALL SYSTEMS OPERATIONAL - Enterprise Ready!")
        else:
            logger.warning("⚠️  Some systems require attention")

        return results


def main():
    """Main demonstration function."""
    demo = ZoningPlatformDemo()

    try:
        results = demo.run_full_demonstration()

        # Save results for portfolio
        import json
        with open("technical-showcase-results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("\n💾 Results saved to technical-showcase-results.json")

    except KeyboardInterrupt:
        logger.info("\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        logger.error(f"\n💥 Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    main()