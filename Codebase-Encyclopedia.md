# NYC Zoning Intelligence Platform - Complete Codebase Encyclopedia

> **Comprehensive reference guide** to understand the full architecture, concepts, and implementation. Use alongside Cursor AI prompts.

---

# TABLE OF CONTENTS

1. **Architecture Overview**
2. **Project Structure & File Organization**
3. **Database Schema & Models**
4. **API Endpoints Reference**
5. **Service Layer & Business Logic**
6. **Frontend Component Structure**
7. **Data Flow Diagrams**
8. **Common Workflows & Patterns**
9. **Testing Strategy**
10. **Deployment Pipeline**
11. **Performance Optimization**
12. **Troubleshooting Guide**
13. **Key Concepts (Zoning, FAR, Tax Incentives)**
14. **Code Patterns & Best Practices**

---

# 1. ARCHITECTURE OVERVIEW

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  React 18 + TypeScript + TailwindCSS + Mapbox GL JS         │
│  ├─ PropertySearch (address input)                           │
│  ├─ PropertyMap (visualization)                              │
│  ├─ ZoningResults (data display)                             │
│  ├─ ReportGenerator (PDF download)                           │
│  └─ Hooks (usePropertyAnalysis, useGeneratePDF, etc.)       │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                      │
│  ├─ /api/properties/* (search, analyze, CRUD)               │
│  ├─ /api/zoning/* (FAR calculations, compliance)            │
│  ├─ /api/landmarks/* (nearby landmarks)                      │
│  ├─ /api/tax-incentives/* (eligibility, valuation)          │
│  ├─ /api/air-rights/* (analysis, transfer opportunities)    │
│  └─ /api/reports/* (PDF generation)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓ Database Queries
┌─────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER (Business Logic)            │
│  ├─ property_service.py (CRUD + geocoding)                  │
│  ├─ zoning_service.py (FAR, height, setback calcs)         │
│  ├─ tax_incentive_service.py (eligibility logic)            │
│  ├─ air_rights_service.py (transfer opportunities)          │
│  └─ spatial_queries.py (all PostGIS operations)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                          │
│  ├─ SQLAlchemy ORM                                           │
│  ├─ GeoAlchemy2 (PostGIS integration)                        │
│  └─ Alembic (migrations)                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              DATABASE LAYER (PostgreSQL + PostGIS)          │
│  ├─ Properties table (lot data + geometry)                   │
│  ├─ ZoningDistricts table (zoning boundaries + rules)       │
│  ├─ PropertyZoning table (many-to-many junction)            │
│  ├─ Landmarks table (historic/cultural sites)               │
│  ├─ TaxIncentivePrograms table (program definitions)        │
│  ├─ PropertyTaxIncentive table (eligibility tracking)       │
│  └─ AirRights table (transfer opportunities)                │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

| Principle | Why It Matters |
|-----------|----------------|
| **Separation of Concerns** | Routes → Services → Spatial Queries → Database |
| **Immutability in Spatial Data** | Geometries never change after creation |
| **Async-First Frontend** | React Query handles loading/caching/errors |
| **Type Safety** | TypeScript (frontend) + Python type hints (backend) |
| **Spatial Indexing** | GIST indexes on all geometry columns = fast queries |
| **Single Responsibility** | Each service handles one domain (zoning, tax incentives, air rights) |

---

# 2. PROJECT STRUCTURE & FILE ORGANIZATION

## Complete Directory Tree

```
zoning-platform/
│
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app initialization
│   │   ├── config.py                 # Environment config, database URL
│   │   ├── database.py               # SQLAlchemy engine, SessionLocal
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── property.py           # Property model
│   │   │   ├── zoning.py             # ZoningDistrict, PropertyZoning models
│   │   │   ├── landmark.py           # Landmark model
│   │   │   ├── tax_incentive.py      # TaxIncentiveProgram, PropertyTaxIncentive
│   │   │   └── air_rights.py         # AirRights model
│   │   │
│   │   ├── schemas/                  # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── property.py           # PropertyCreate, PropertyResponse
│   │   │   ├── zoning.py             # ZoningDistrictResponse, etc.
│   │   │   ├── landmark.py           # LandmarkResponse
│   │   │   ├── tax_incentive.py      # TaxIncentiveResponse
│   │   │   ├── analysis.py           # PropertyAnalysisResponse (combined)
│   │   │   └── report.py             # PDFReportRequest
│   │   │
│   │   ├── api/                      # Route handlers
│   │   │   ├── __init__.py
│   │   │   ├── routes.py             # Main router combining all sub-routers
│   │   │   ├── properties.py         # GET/POST /api/properties/*
│   │   │   ├── zoning.py             # GET /api/zoning/*
│   │   │   ├── landmarks.py          # GET /api/landmarks/*
│   │   │   ├── tax_incentives.py     # GET /api/tax-incentives/*
│   │   │   ├── air_rights.py         # GET /api/air-rights/*
│   │   │   └── reports.py            # POST /api/reports/generate-pdf
│   │   │
│   │   ├── services/                 # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── property_service.py   # Property CRUD + geocoding
│   │   │   ├── zoning_service.py     # FAR, height, setback logic
│   │   │   ├── tax_incentive_service.py # Eligibility calculations
│   │   │   ├── air_rights_service.py # Transfer opportunity analysis
│   │   │   └── spatial_queries.py    # All PostGIS queries
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── geocoding.py          # Address → coordinates
│   │   │   ├── pdf_generator.py      # Report PDF generation
│   │   │   └── constants.py          # Zoning rules, tax incentive defs
│   │   │
│   │   ├── core/                     # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # Auth, API key validation
│   │   │   └── logging.py            # Logging configuration
│   │   │
│   │   └── dependencies.py           # FastAPI dependency injection
│   │
│   ├── migrations/                   # Alembic database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 0001_initial.py       # Initial schema creation
│   │
│   ├── tests/                        # Unit & integration tests
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest fixtures
│   │   ├── test_models.py            # Model tests
│   │   ├── test_services.py          # Service layer tests
│   │   ├── test_api.py               # API endpoint tests
│   │   └── test_spatial_queries.py   # PostGIS query tests
│   │
│   ├── .dockerignore
│   ├── Dockerfile                    # Production Docker image
│   ├── docker-compose.yml            # Local dev: FastAPI + PostgreSQL
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Example environment variables
│   ├── pyproject.toml                # Project metadata, tool config
│   └── README.md
│
├── frontend/                         # React/TypeScript frontend
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── PropertySearch.tsx    # Address search bar
│   │   │   ├── PropertyMap.tsx       # Mapbox GL visualization
│   │   │   ├── ZoningResults.tsx     # Results dashboard
│   │   │   ├── ReportGenerator.tsx   # PDF report UI
│   │   │   ├── LandmarksList.tsx     # Nearby landmarks list
│   │   │   ├── LoadingState.tsx      # Spinner/skeleton loading
│   │   │   └── ErrorBoundary.tsx     # Error handling wrapper
│   │   │
│   │   ├── pages/                    # Next.js/React Router pages
│   │   │   ├── index.tsx             # Home page (search)
│   │   │   ├── analysis.tsx          # Results page
│   │   │   ├── _app.tsx              # App wrapper
│   │   │   └── _document.tsx         # HTML wrapper
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── usePropertyAnalysis.ts    # Fetch property analysis
│   │   │   ├── useSearchProperties.ts    # Search properties
│   │   │   ├── useGeneratePDF.ts        # Generate PDF report
│   │   │   ├── useMap.ts                # Mapbox GL initialization
│   │   │   └── useApi.ts                # Generic API wrapper
│   │   │
│   │   ├── services/                 # API client services
│   │   │   ├── api.ts                # Axios instance + base config
│   │   │   └── mapbox.ts             # Mapbox GL configuration
│   │   │
│   │   ├── types/                    # TypeScript type definitions
│   │   │   ├── index.ts              # Main type exports
│   │   │   ├── property.ts           # Property-related types
│   │   │   ├── zoning.ts             # Zoning-related types
│   │   │   ├── api.ts                # API response types
│   │   │   └── mapbox.ts             # Mapbox-specific types
│   │   │
│   │   ├── styles/                   # Global CSS
│   │   │   └── globals.css           # Tailwind imports + globals
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   ├── constants.ts          # API_URL, colors, etc.
│   │   │   ├── formatters.ts         # Currency, distance formatting
│   │   │   └── validators.ts         # Input validation
│   │   │
│   │   └── layout.tsx                # Main layout component
│   │
│   ├── public/                       # Static assets
│   │   └── favicon.ico
│   │
│   ├── .env.local.example            # Example env vars
│   ├── next.config.js                # Next.js config
│   ├── tailwind.config.js            # Tailwind CSS config
│   ├── tsconfig.json                 # TypeScript config
│   ├── package.json                  # Dependencies
│   ├── package-lock.json
│   └── README.md
│
├── .gitignore
├── docker-compose.yml                # Orchestration (both services)
├── README.md                         # Project overview
└── .github/
    └── workflows/
        └── deploy.yml                # CI/CD pipeline
```

---

# 3. DATABASE SCHEMA & MODELS

## Entity-Relationship Diagram

```
┌──────────────────┐
│   Properties     │
│                  │
│ id (PK)          │
│ address          │◄──────────────────┐
│ lot_number       │                   │ 1
│ block_number     │                   │ :
│ geom (POINT)     │                   │ M
│ land_area_sf     │                   │
│ building_area_sf │                   │
│ current_use      │                   │
└──────────────────┘                   │
                                       │
                   ┌─────────────────────────────────┐
                   │   PropertyZoning (junction)     │
                   │                                 │
                   │ property_id (FK)                │
                   │ zoning_district_id (FK)         │
                   │ percent_in_district             │
                   └─────────────────────────────────┘
                                       │
                   ┌─────────────────────┐
                   │                     │ M
                   │                     │ :
                   │                     │ 1
              ┌────────────────────┐
              │  ZoningDistricts   │
              │                    │
              │ id (PK)            │
              │ district_code      │
              │ district_name      │
              │ geom (MULTIPOLYGON)│
              │ far_base           │
              │ far_with_bonus     │
              │ max_height_ft      │
              │ setback_requirements│
              └────────────────────┘

┌──────────────────────────────────────┐
│   TaxIncentivePrograms               │
│                                      │
│ id (PK)                              │
│ program_code (e.g., "467-M")        │
│ program_name                         │◄─────────────────┐
│ description                          │                  │ 1
│ eligible_zoning_districts (JSON)     │                  │ :
│ min_building_age                     │                  │ M
│ requires_residential                 │                  │
│ tax_abatement_years                  │                  │
└──────────────────────────────────────┘                  │
                                                          │
                            ┌────────────────────────────────┐
                            │  PropertyTaxIncentive (junction)│
                            │                                │
                            │ property_id (FK)               │
                            │ tax_incentive_id (FK)          │
                            │ is_eligible                    │
                            │ eligibility_reason             │
                            │ estimated_abatement_value      │
                            └────────────────────────────────┘

┌──────────────────┐
│  Landmarks       │
│                  │
│ id (PK)          │
│ name             │
│ landmark_type    │
│ geom (POINT)     │
│ description      │
└──────────────────┘

┌──────────────────┐
│  AirRights       │
│                  │
│ id (PK)          │
│ property_id (FK) │◄─────── 1:1 with Properties
│ unused_far       │
│ transferable_far │
│ adj_properties   │
│ tdr_price        │
└──────────────────┘
```

## Key Tables Overview

**Properties Table**: Stores property lot data with geometry (POINT).
- Indexed on address for fast lookups
- GIST spatial index on geom for fast location queries
- land_area_sf used for FAR calculations

**ZoningDistricts Table**: Stores zoning district boundaries and rules.
- geom is MULTIPOLYGON (can be multiple polygons per district)
- far_base and far_with_bonus define building potential
- max_height_ft and setback_requirements define constraints
- GIST spatial index for fast intersection queries

**PropertyZoning Junction**: Maps properties to their zoning districts.
- Property can span multiple districts (percent_in_district tracks split)
- Used for weighted FAR calculations
- Unique constraint on (property_id, zoning_district_id)

**Landmarks Table**: Historic and cultural sites near properties.
- geom is POINT for specific location
- GIST spatial index for fast distance queries (ST_DWithin)

**TaxIncentivePrograms & PropertyTaxIncentive**: Eligibility tracking.
- Programs defined once (467-M, ICAP, etc.)
- PropertyTaxIncentive tracks eligibility per property
- estimated_abatement_value calculated based on program rules

**AirRights Table**: Transfer Development Rights analysis.
- One-to-one with Properties
- Calculated fields: unused_far, transferable_far
- adjacent_property_ids stored as JSON array for recipients

---

# 4. API ENDPOINTS REFERENCE

## Endpoint Categories

### Properties Endpoints

```
POST /api/properties/analyze
  └─ Full analysis: geocode → create property → find zoning → check incentives → calc air rights

GET /api/properties/{property_id}
  └─ Return single property details

GET /api/properties/search?address=...&city=...&state=...
  └─ Search by address, return nearby properties
```

### Zoning Endpoints

```
GET /api/properties/{property_id}/zoning
  └─ Complete zoning analysis for property

POST /api/zoning/far-calculator
  └─ Calculate FAR given lot area and zoning codes

GET /api/properties/{property_id}/zoning/compliance
  └─ Check if proposed building meets zoning requirements
```

### Landmarks Endpoints

```
GET /api/properties/{property_id}/landmarks?distance_ft=150
  └─ Find landmarks within distance

GET /api/landmarks/by-type?type=historic&distance_ft=150
  └─ Filter landmarks by type
```

### Tax Incentives Endpoints

```
GET /api/properties/{property_id}/tax-incentives
  └─ List all eligible tax programs

GET /api/properties/{property_id}/tax-incentives/{program_code}
  └─ Detailed eligibility info for specific program
```

### Air Rights Endpoints

```
GET /api/properties/{property_id}/air-rights
  └─ Current air rights analysis

GET /api/properties/{property_id}/air-rights/recipients
  └─ Properties that can receive air rights
```

### Reports Endpoints

```
POST /api/reports/generate-pdf
  └─ Generate and download PDF report

POST /api/reports/preview
  └─ Preview report data (no PDF)
```

---

# 5. SERVICE LAYER & BUSINESS LOGIC

## Service Organization

| Service | Responsibility | Key Functions |
|---------|----------------|----------------|
| **spatial_queries.py** | All PostGIS operations | ST_Intersects, ST_DWithin, distance calcs |
| **zoning_service.py** | FAR, height, setback logic | FAR calculations, compliance checks |
| **tax_incentive_service.py** | Eligibility & valuation | 467-M checks, abatement estimates |
| **air_rights_service.py** | Transfer opportunities | Unused FAR, recipient analysis |
| **property_service.py** | CRUD + orchestration | Create, search, full analysis |

## Core Service Flows

### Property Analysis Flow

```python
get_property_full_analysis(property_id)
├─ zoning_service.analyze_property_zoning()
│  ├─ spatial_queries.find_zoning_districts()
│  │  └─ ST_Intersects(zoning_geom, property_geom) [uses GIST index]
│  └─ Calculate weighted FAR by percentage
├─ tax_incentive_service.check_eligibility()
│  ├─ Check zoning eligibility
│  ├─ Check building age
│  └─ Estimate abatement value
├─ air_rights_service.analyze_air_rights()
│  ├─ Calculate unused FAR
│  └─ Find adjacent properties
└─ spatial_queries.find_nearby_landmarks()
   └─ ST_DWithin(landmarks.geom, property.geom, 150ft) [uses GIST index]
```

---

# 6. FRONTEND COMPONENT STRUCTURE

## Component Hierarchy

```
_app.tsx (React Query setup, global providers)
  ↓
index.tsx (Home page)
  └─ PropertySearch
      └─ On select → navigate to analysis page
          ↓
analysis.tsx (Results page)
  ├─ PropertyMap (left side)
  │  └─ Mapbox GL with layers: property, zoning, landmarks
  ├─ ZoningResults (right side, scrollable)
  │  ├─ Property info
  │  ├─ Zoning cards (per district)
  │  ├─ Tax incentive cards
  │  ├─ Air rights summary
  │  └─ Landmarks table
  └─ ReportGenerator (button at bottom)
      └─ Generate & download PDF
```

## Component Data Flow

```
User types address
    ↓
PropertySearch.tsx (debounced search)
    ↓
useApi hook calls GET /api/properties/search
    ↓
Display suggestions
    ↓
User clicks property
    ↓
Navigate to analysis.tsx?property_id=uuid
    ↓
usePropertyAnalysis hook (React Query) calls GET /api/analysis
    ↓
Display PropertyMap + ZoningResults (from cache)
    ↓
User clicks "Generate PDF"
    ↓
ReportGenerator calls POST /api/reports/generate-pdf
    ↓
Browser downloads PDF
```

## Key Hooks

```typescript
usePropertyAnalysis(propertyId)
  └─ Fetches: property, zoning, tax incentives, landmarks, air rights

useSearchProperties(searchTerm)
  └─ Debounced search for addresses

useGeneratePDF(propertyId, options)
  └─ Generates and downloads PDF report

useMap(mapContainer, analysis)
  └─ Initialize Mapbox GL with property data
```

---

# 7. COMMON WORKFLOWS & PATTERNS

## Pattern 1: Spatial Query with Index

```python
# ✅ CORRECT: Uses GIST index for fast O(log n) lookup
districts = session.query(ZoningDistrict).filter(
    ST_Intersects(ZoningDistrict.geom, property.geom)
).all()

# ❌ SLOW: No index, O(n) sequential scan
# Don't do this: for each zoning in all_zonings: if touches(zoning, property)
```

## Pattern 2: Service Composition

```python
# Route just calls orchestrator service
@router.get("/api/analysis/{id}")
async def analyze(id: UUID, session: Session = Depends(get_db)):
    return property_service.get_property_full_analysis(id, session)

# Service composes other services
def get_property_full_analysis(id, session):
    zoning = zoning_service.analyze(id, session)
    tax = tax_incentive_service.check(id, session)
    air = air_rights_service.analyze(id, session)
    return combine(zoning, tax, air)
```

## Pattern 3: Type Safety

```python
def calculate_far(
    property_id: UUID,
    include_bonuses: bool = True,
    session: Session = Depends(get_db)
) -> float:
    """Calculate FAR as numeric value."""
    # Implementation
    return float_value
```

## Pattern 4: Error Handling

```python
def get_property(property_id: UUID, session: Session) -> Property:
    prop = session.query(Property).filter_by(id=property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Not found")
    return prop
```

## Pattern 5: React Query with Cache

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['property', id],
  queryFn: () => api.get(`/properties/${id}`),
  staleTime: 5 * 60 * 1000, // 5 min cache
  enabled: !!id // Only fetch if id exists
})
```

---

# 8. DATA FLOW DIAGRAMS

## Complete User Journey

```
┌──────────────────┐
│  User searches   │
│  address         │
└─────────┬────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ PropertySearch.tsx                                       │
│ - Input: "123 Main St"                                   │
│ - Debounce 300ms                                         │
│ - Call: GET /properties/search?address=...               │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ FastAPI Route: properties.py                             │
│ - Geocode address to coordinates                         │
│ - Call: property_service.search_by_address()             │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ PropertyService                                          │
│ - Call: spatial_queries.get_property_by_address()        │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ SpatialQueries                                           │
│ - ST_DWithin(properties.geom, geocoded_point, 50m)       │
│ - Uses GIST index: O(log n) ✓                            │
│ - Returns: Property[] within 50 feet                     │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ PostgreSQL + PostGIS                                     │
│ - GIST index lookup: ~1ms                                │
│ - Return results to FastAPI                              │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ Frontend                                                 │
│ - Display property suggestions                           │
│ - User clicks property → navigate to analysis page       │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ analysis.tsx                                             │
│ - usePropertyAnalysis(propertyId) hook                   │
│ - Fetch: GET /api/properties/{id}/analysis               │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ FastAPI Route: analysis endpoint                         │
│ - Call: property_service.get_property_full_analysis()    │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ PropertyService orchestrator                             │
│ ├─ zoning_service.analyze()                              │
│ │  ├─ spatial_queries.find_zoning_districts()           │
│ │  │  └─ ST_Intersects with GIST: O(log n)              │
│ │  └─ Calculate weighted FAR                             │
│ │                                                        │
│ ├─ tax_incentive_service.check_eligibility()            │
│ │  ├─ Check zoning district codes                       │
│ │  ├─ Check building age                                │
│ │  └─ Estimate abatement value                          │
│ │                                                        │
│ ├─ air_rights_service.analyze()                         │
│ │  ├─ Calculate unused FAR                              │
│ │  └─ Find adjacent properties (ST_Touches)             │
│ │                                                        │
│ └─ spatial_queries.find_nearby_landmarks()              │
│    └─ ST_DWithin with GIST: O(log n)                    │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ Response: PropertyAnalysisResponse                       │
│ - Property details                                       │
│ - Zoning districts (with FAR, height, setbacks)          │
│ - Tax incentives (with eligibility, estimated value)     │
│ - Air rights (with unused FAR, recipients)               │
│ - Nearby landmarks (with distances)                      │
└─────────┬──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────────────────┐
│ Frontend: Display Results                                │
│ ├─ PropertyMap.tsx                                       │
│ │  ├─ Render property geometry (POINT)                   │
│ │  ├─ Overlay zoning district boundaries (colored)       │
│ │  ├─ Add landmark pins                                  │
│ │  └─ Zoom to property                                   │
│ │                                                        │
│ ├─ ZoningResults.tsx                                     │
│ │  ├─ Display zoning districts with FAR, height         │
│ │  ├─ Display eligible tax programs                     │
│ │  ├─ Display air rights summary                        │
│ │  └─ Display landmarks table                           │
│ │                                                        │
│ └─ ReportGenerator.tsx                                  │
│    └─ "Generate PDF" button                             │
└──────────────────────────────────────────────────────────┘
```

---

# 9. TESTING STRATEGY

## Backend Testing

### Fixtures

```python
@pytest.fixture
def test_property(session):
    """Create test property at known coordinates"""
    prop = Property(
        address="123 Test St",
        lot_number="123-ABC",
        land_area_sf=5000,
        geom=WKTElement("POINT(-74.0060 40.7128)", srid=4326)
    )
    session.add(prop)
    session.commit()
    return prop

@pytest.fixture
def test_zoning(session):
    """Create test zoning district containing property"""
    zone = ZoningDistrict(
        district_code="R10",
        far_base=10.0,
        geom=WKTElement(
            "MULTIPOLYGON(((-74.0100 40.7100, -74.0020 40.7100, "
            "-74.0020 40.7150, -74.0100 40.7150, -74.0100 40.7100)))",
            srid=4326
        )
    )
    session.add(zone)
    session.commit()
    return zone
```

### Test Cases

```python
# Test spatial query
def test_find_zoning_districts(session, test_property, test_zoning):
    districts = spatial_queries.find_zoning_districts(test_property.geom, session)
    assert len(districts) == 1
    assert districts[0]['district_code'] == "R10"

# Test service logic
def test_calculate_far_with_bonuses(session, test_property, test_zoning):
    far = zoning_service.calculate_far_with_bonuses(test_property.id, session)
    assert far == 10.0

# Test API endpoint
def test_analyze_property_endpoint(client, test_property):
    response = client.get(f"/api/properties/{test_property.id}/analysis")
    assert response.status_code == 200
    data = response.json()
    assert 'zoning' in data
    assert 'tax_incentives' in data
    assert 'air_rights' in data
```

## Frontend Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { PropertySearch } from '@/components/PropertySearch'

test('should search properties on address input', async () => {
  const mockOnSelect = jest.fn()
  render(<PropertySearch onPropertySelect={mockOnSelect} />)
  
  const input = screen.getByPlaceholderText('Enter NYC address...')
  fireEvent.change(input, { target: { value: '123 Main' } })
  
  await waitFor(() => {
    expect(screen.getByText('123 Main St')).toBeInTheDocument()
  })
})
```

---

# 10. DEPLOYMENT PIPELINE

## Local Development

```bash
# Start all services
docker-compose up

# Services available at:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: localhost:5432
```

## Production Deployment

### Backend → Render.com

```yaml
services:
  - type: web
    name: zoning-api
    env: docker
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: zoning-db
          property: connectionString
```

### Frontend → Vercel

```bash
# Environment variables:
# NEXT_PUBLIC_API_URL=https://zoning-api.onrender.com
# NEXT_PUBLIC_MAPBOX_TOKEN=pk_...

# Vercel auto-deploys on git push to main
```

### Database → Render PostgreSQL with PostGIS

```yaml
services:
  - type: pserv
    name: zoning-db
    postgresVersion: 15
    extensions:
      - postgis
```

### CI/CD → GitHub Actions

```yaml
on: [push to main]
jobs:
  test:
    - Run pytest on backend
    - Run jest on frontend
  deploy:
    - Deploy backend to Render
    - Deploy frontend to Vercel
    - Run database migrations
```

---

# 11. PERFORMANCE OPTIMIZATION

## Database Optimizations

| Optimization | Impact | Implementation |
|-------------|--------|-----------------|
| **GIST Spatial Indexes** | 100x faster spatial queries | `CREATE INDEX ON table USING GIST(geom)` |
| **Selective Column Queries** | Faster data transfer | `SELECT id, code, far_base` not `SELECT *` |
| **React Query Caching** | Eliminate refetches | `staleTime: 5 * 60 * 1000` |
| **Connection Pooling** | Reuse connections | SQLAlchemy pool_size |
| **Batch Operations** | 100x faster inserts | `bulk_insert_mappings()` |

## Frontend Optimizations

- React Query caching (staleTime = 5 min default)
- Code splitting with Next.js
- Image optimization
- Debouncing search input (300ms)
- Layer visibility toggles in Mapbox

---

# 12. TROUBLESHOOTING GUIDE

## Common Issues

### Issue: Slow ST_Intersects queries

```bash
# Check if GIST index exists
SELECT * FROM pg_indexes WHERE tablename = 'zoning_districts';

# If missing, create it
CREATE INDEX idx_zoning_geom ON zoning_districts USING GIST(geom);

# Analyze query plan
EXPLAIN ANALYZE
SELECT * FROM zoning_districts
WHERE ST_Intersects(geom, ST_Point(-74.0060, 40.7128));
```

### Issue: Geometry parsing error

```python
from shapely.geometry import Point
try:
    point = Point(-74.0060, 40.7128)
    geom = WKTElement(f"POINT({point.x} {point.y})", srid=4326)
except Exception as e:
    print(f"Invalid: {e}")
```

### Issue: React Query not updating

```typescript
// Option 1: Shorter staleTime
useQuery({
  staleTime: 1 * 60 * 1000 // 1 min instead of 5
})

// Option 2: Manual invalidation
const { invalidateQueries } = useQueryClient()
invalidateQueries({ queryKey: ['property', id] })
```

---

# 13. KEY CONCEPTS

## Floor Area Ratio (FAR)

```
FAR = Maximum Allowed Building Area / Lot Area

Example:
- Lot: 5,000 SF
- Zoning: R10 (FAR 10.0)
- Max building area: 5,000 × 10.0 = 50,000 SF

With City of Yes bonus (20% FAR increase):
- New FAR: 10.0 × 1.2 = 12.0
- New max: 5,000 × 12.0 = 60,000 SF
```

## Setbacks

```
Setback = Minimum distance building must be from lot edge

- Front setback: 25 ft from street
- Side setback: 5 ft from side property lines
- Rear setback: 10 ft from rear property line
```

## 467-M Tax Abatement Program

```
Purpose: Encourage residential conversion of commercial buildings

Requirements:
1. In eligible zoning (C4-7, C6-4, M1-1, etc.)
2. Building 20+ years old
3. Convert to residential

Benefit:
- 85% tax reduction for 10 years
- 75% tax reduction for next 15 years
- Total: 25 years of tax savings
```

## Air Rights (Transfer Development Rights)

```
Concept: Transfer unused building potential from one lot to adjacent lot

Scenario:
- Historic building on valuable lot
- Can't demolish (landmark)
- Building uses 4 FAR of 10 FAR allowed
- Unused FAR = 6.0 → can sell to adjacent property
- Market price: ~$125/SF of transferable air
```

---

# 14. BEST PRACTICES & PATTERNS

## ✅ DO

- Use services for all business logic (routes just call services)
- Type everything (Python type hints + TypeScript)
- Use spatial indexes (GIST on all geometry columns)
- Cache with React Query (staleTime for repeated queries)
- Test with fixtures and mocks
- Commit frequently with clear messages
- Document with docstrings and comments

## ❌ DON'T

- Put business logic in route handlers
- Write SQL directly (use SQLAlchemy ORM)
- Ignore error handling (always raise HTTPException)
- Query without spatial indexes
- Mutate shared state in React
- Hardcode API URLs or colors
- Deploy without testing

---

## Final Checklist

After reading this encyclopedia, you should understand:

- [ ] Database schema and relationships
- [ ] Spatial queries (ST_Intersects, ST_DWithin) and GIST indexes
- [ ] Service layer abstraction: routes → services → queries → database
- [ ] FAR calculations, tax incentives, air rights analysis
- [ ] React component hierarchy and data flow
- [ ] User journey from search to results to PDF
- [ ] Testing patterns and fixtures
- [ ] Deployment to Render + Vercel
- [ ] Performance optimizations
- [ ] NYC real estate domain concepts

**You're ready to build.** Use with Cursor AI prompts, iterate locally, and ship.
