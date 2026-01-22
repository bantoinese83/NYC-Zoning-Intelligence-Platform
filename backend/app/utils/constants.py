"""
Application constants and configuration data.

Contains zoning rules, tax incentive definitions, and other
static data used throughout the application.
"""

from decimal import Decimal
from typing import Dict

# Zoning district configurations
ZONING_DISTRICTS = {
    # Residential districts
    "R1-1": {
        "category": "residential",
        "base_far": Decimal("0.5"),
        "max_height_ft": 30,
    },
    "R1-2": {
        "category": "residential",
        "base_far": Decimal("0.75"),
        "max_height_ft": 35,
    },
    "R2": {"category": "residential", "base_far": Decimal("1.0"), "max_height_ft": 35},
    "R2A": {"category": "residential", "base_far": Decimal("1.0"), "max_height_ft": 35},
    "R2X": {"category": "residential", "base_far": Decimal("1.0"), "max_height_ft": 35},
    "R3-1": {
        "category": "residential",
        "base_far": Decimal("1.25"),
        "max_height_ft": 60,
    },
    "R3-2": {
        "category": "residential",
        "base_far": Decimal("2.0"),
        "max_height_ft": 75,
    },
    "R3X": {"category": "residential", "base_far": Decimal("2.0"), "max_height_ft": 75},
    "R4": {"category": "residential", "base_far": Decimal("3.0"), "max_height_ft": 120},
    "R4-1": {
        "category": "residential",
        "base_far": Decimal("3.0"),
        "max_height_ft": 120,
    },
    "R4A": {
        "category": "residential",
        "base_far": Decimal("3.0"),
        "max_height_ft": 120,
    },
    "R5": {"category": "residential", "base_far": Decimal("4.0"), "max_height_ft": 120},
    # Commercial districts
    "C1-6": {"category": "commercial", "base_far": Decimal("3.0"), "max_height_ft": 75},
    "C1-7": {"category": "commercial", "base_far": Decimal("3.0"), "max_height_ft": 75},
    "C1-8": {"category": "commercial", "base_far": Decimal("3.0"), "max_height_ft": 75},
    "C1-9": {"category": "commercial", "base_far": Decimal("3.0"), "max_height_ft": 75},
    "C2-6": {"category": "commercial", "base_far": Decimal("3.0"), "max_height_ft": 75},
    "C2-7": {"category": "commercial", "base_far": Decimal("3.0"), "max_height_ft": 75},
    "C2-8": {
        "category": "commercial",
        "base_far": Decimal("6.0"),
        "max_height_ft": 120,
    },
    "C4-6": {
        "category": "commercial",
        "base_far": Decimal("6.0"),
        "max_height_ft": 120,
    },
    "C4-7": {
        "category": "commercial",
        "base_far": Decimal("6.0"),
        "max_height_ft": 120,
    },
    "C5-1": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C5-2": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C5-3": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C6-1": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C6-2": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C6-3": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C6-4": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    "C6-5": {
        "category": "commercial",
        "base_far": Decimal("10.0"),
        "max_height_ft": 150,
    },
    # Manufacturing districts
    "M1-1": {
        "category": "manufacturing",
        "base_far": Decimal("2.0"),
        "max_height_ft": 60,
    },
    "M1-2": {
        "category": "manufacturing",
        "base_far": Decimal("2.0"),
        "max_height_ft": 60,
    },
    "M1-3": {
        "category": "manufacturing",
        "base_far": Decimal("2.0"),
        "max_height_ft": 60,
    },
    "M1-4": {
        "category": "manufacturing",
        "base_far": Decimal("2.0"),
        "max_height_ft": 60,
    },
    "M1-5": {
        "category": "manufacturing",
        "base_far": Decimal("2.0"),
        "max_height_ft": 60,
    },
    "M1-6": {
        "category": "manufacturing",
        "base_far": Decimal("2.0"),
        "max_height_ft": 60,
    },
    "M2-1": {
        "category": "manufacturing",
        "base_far": Decimal("3.0"),
        "max_height_ft": 75,
    },
    "M2-2": {
        "category": "manufacturing",
        "base_far": Decimal("3.0"),
        "max_height_ft": 75,
    },
    "M2-3": {
        "category": "manufacturing",
        "base_far": Decimal("3.0"),
        "max_height_ft": 75,
    },
    "M2-4": {
        "category": "manufacturing",
        "base_far": Decimal("3.0"),
        "max_height_ft": 75,
    },
    "M3-1": {
        "category": "manufacturing",
        "base_far": Decimal("5.0"),
        "max_height_ft": 120,
    },
    "M3-2": {
        "category": "manufacturing",
        "base_far": Decimal("5.0"),
        "max_height_ft": 120,
    },
}


# City of Yes FAR bonuses by zoning district
CITY_OF_YES_BONUSES = {
    "R6": Decimal("1.5"),  # 50% bonus
    "R7": Decimal("1.5"),
    "R8": Decimal("1.5"),
    "R9": Decimal("1.5"),
    "R10": Decimal("2.0"),  # 100% bonus
    "C1": Decimal("1.5"),
    "C2": Decimal("1.5"),
    "C3": Decimal("1.5"),
    "C4": Decimal("1.5"),
    "C5": Decimal("1.5"),
    "C6": Decimal("1.5"),
}


# Tax incentive program configurations
TAX_INCENTIVE_PROGRAMS = {
    "467-M": {
        "name": "Residential Conversion Tax Abatement",
        "eligible_zoning": ["C4-7", "C6-4", "M1-1", "M1-2", "M2-1", "M2-2"],
        "min_building_age_years": 20,
        "requires_residential_conversion": True,
        "tax_abatement_years": 25,
        "abatement_schedule": {
            "years_1_10": 0.85,  # 85% abatement
            "years_11_25": 0.75,  # 75% abatement
        },
        "description": "Tax abatement for converting commercial/industrial buildings to residential use",
    },
    "ICAP": {
        "name": "Industrial & Commercial Abatement Program",
        "eligible_zoning": ["M1", "M2", "M3", "C4", "C5", "C6"],
        "min_building_age_years": None,
        "requires_residential_conversion": False,
        "tax_abatement_years": 15,
        "abatement_schedule": {"years_1_15": 0.25},  # 25% abatement
        "description": "Tax abatement for industrial and commercial properties",
    },
    "421-A": {
        "name": "Residential Property Tax Exemption",
        "eligible_zoning": ["R1", "R2", "R3", "R4", "R5", "R6"],
        "min_building_age_years": None,
        "requires_residential_conversion": False,
        "tax_abatement_years": 10,
        "abatement_schedule": {"years_1_10": 1.0},  # 100% exemption
        "description": "Tax exemption for new residential construction",
    },
    "421-G": {
        "name": "Transit-Oriented Development Exemption",
        "eligible_zoning": [
            "R6",
            "R7",
            "R8",
            "R9",
            "R10",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "C6",
        ],
        "min_building_age_years": None,
        "requires_residential_conversion": False,
        "tax_abatement_years": 20,
        "abatement_schedule": {"years_1_20": 1.0},  # 100% exemption
        "description": "Tax exemption for development near transit stations",
    },
}


# Landmark types and their significance
LANDMARK_TYPES = {
    "historic": {
        "description": "Historic buildings and districts protected by landmarks law",
        "significance": "high",
        "impact_on_development": "severe_restrictions",
    },
    "cultural": {
        "description": "Culturally significant sites and institutions",
        "significance": "medium",
        "impact_on_development": "moderate_restrictions",
    },
    "natural": {
        "description": "Natural features and protected green spaces",
        "significance": "medium",
        "impact_on_development": "moderate_restrictions",
    },
    "transportation": {
        "description": "Transportation infrastructure and historic stations",
        "significance": "low",
        "impact_on_development": "minor_restrictions",
    },
    "religious": {
        "description": "Religious institutions and historic houses of worship",
        "significance": "high",
        "impact_on_development": "severe_restrictions",
    },
    "educational": {
        "description": "Educational institutions and historic schools",
        "significance": "medium",
        "impact_on_development": "moderate_restrictions",
    },
}


# Setback requirements by zoning district (in feet)
SETBACK_REQUIREMENTS = {
    "front": {
        "R1": 10,
        "R2": 10,
        "R3": 10,
        "R4": 10,
        "R5": 10,
        "C1": 10,
        "C2": 10,
        "C3": 10,
        "C4": 10,
        "C5": 15,
        "C6": 15,
        "M1": 10,
        "M2": 10,
        "M3": 15,
    },
    "side": {
        "R1": 5,
        "R2": 5,
        "R3": 5,
        "R4": 5,
        "R5": 5,
        "C1": 5,
        "C2": 5,
        "C3": 5,
        "C4": 5,
        "C5": 8,
        "C6": 8,
        "M1": 5,
        "M2": 5,
        "M3": 8,
    },
    "rear": {
        "R1": 5,
        "R2": 5,
        "R3": 5,
        "R4": 5,
        "R5": 5,
        "C1": 5,
        "C2": 5,
        "C3": 5,
        "C4": 5,
        "C5": 10,
        "C6": 10,
        "M1": 5,
        "M2": 5,
        "M3": 10,
    },
}


# Air rights market data (placeholder values)
AIR_RIGHTS_MARKET_DATA = {
    "manhattan": {
        "average_price_per_sf": 150.00,
        "price_range": [100.00, 300.00],
        "recent_transactions_count": 45,
    },
    "brooklyn": {
        "average_price_per_sf": 95.00,
        "price_range": [60.00, 150.00],
        "recent_transactions_count": 23,
    },
    "queens": {
        "average_price_per_sf": 85.00,
        "price_range": [50.00, 130.00],
        "recent_transactions_count": 12,
    },
    "bronx": {
        "average_price_per_sf": 75.00,
        "price_range": [40.00, 120.00],
        "recent_transactions_count": 8,
    },
    "staten_island": {
        "average_price_per_sf": 70.00,
        "price_range": [35.00, 110.00],
        "recent_transactions_count": 5,
    },
}


# API rate limits
RATE_LIMITS = {
    "anonymous": {"requests_per_minute": 60, "requests_per_hour": 1000},
    "authenticated": {"requests_per_minute": 300, "requests_per_hour": 5000},
    "premium": {"requests_per_minute": 1000, "requests_per_hour": 20000},
}


# Coordinate reference systems
CRS_WGS84 = 4326  # WGS84 latitude/longitude
CRS_NAD83 = 2263  # NAD83 / New York Long Island (feet)


# Property use codes (simplified)
PROPERTY_USE_CODES = {
    "0100": "Residential",
    "0200": "Office",
    "0300": "Retail",
    "0400": "Manufacturing",
    "0500": "Hotel",
    "0600": "Parking",
    "0700": "Vacant",
    "0800": "Recreation",
    "0900": "Government",
    "1000": "Religious",
    "1100": "Educational",
    "1200": "Hospital",
    "1300": "Transportation",
}


# Borough codes
BOROUGH_CODES = {
    1: "Manhattan",
    2: "Bronx",
    3: "Brooklyn",
    4: "Queens",
    5: "Staten Island",
}


# Tax class codes
TAX_CLASS_CODES = {
    "1": "Residential (1-3 family)",
    "2": "Residential (Condo/Apt)",
    "3": "Utility",
    "4": "Commercial/Industrial",
}


def get_zoning_far(district_code: str, include_bonuses: bool = False) -> Decimal:
    """
    Get FAR for a zoning district.

    Args:
        district_code: Zoning district code
        include_bonuses: Whether to include City of Yes bonuses

    Returns:
        FAR as Decimal
    """
    district_info = ZONING_DISTRICTS.get(district_code, {})
    far = district_info.get("base_far", Decimal("0"))

    if include_bonuses:
        # Check for City of Yes bonus
        bonus_multiplier = Decimal("1.0")
        for prefix, multiplier in CITY_OF_YES_BONUSES.items():
            if district_code.startswith(prefix):
                bonus_multiplier = multiplier
                break
        far *= bonus_multiplier

    return far


def get_zoning_category(district_code: str) -> str:
    """
    Get zoning district category.

    Args:
        district_code: Zoning district code

    Returns:
        Category string
    """
    district_info = ZONING_DISTRICTS.get(district_code, {})
    return district_info.get("category", "unknown")


def get_setbacks_for_district(district_code: str) -> Dict[str, int]:
    """
    Get setback requirements for a zoning district.

    Args:
        district_code: Zoning district code

    Returns:
        Dictionary with front, side, rear setbacks
    """
    # Extract district prefix (e.g., "R10" -> "R1", "C6-4" -> "C6")
    prefix = district_code.split("-")[0]

    return {
        "front_ft": SETBACK_REQUIREMENTS["front"].get(prefix, 10),
        "side_ft": SETBACK_REQUIREMENTS["side"].get(prefix, 5),
        "rear_ft": SETBACK_REQUIREMENTS["rear"].get(prefix, 5),
    }


def is_eligible_for_incentive(district_code: str, program_code: str) -> bool:
    """
    Check if a zoning district is eligible for a tax incentive program.

    Args:
        district_code: Zoning district code
        program_code: Tax incentive program code

    Returns:
        True if eligible, False otherwise
    """
    program_config = TAX_INCENTIVE_PROGRAMS.get(program_code, {})
    eligible_zoning = program_config.get("eligible_zoning", [])

    # Check if district matches any eligible pattern
    for eligible in eligible_zoning:
        if district_code.startswith(eligible):
            return True

    return False
