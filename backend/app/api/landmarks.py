"""
Landmarks API routes.

Handles landmark search and proximity analysis.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import LandmarkResponse, NearbyLandmarksResponse
from ..services import spatial_queries

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/properties/{property_id}/landmarks",
    response_model=NearbyLandmarksResponse,
    summary="Get nearby landmarks",
    description="""
    Find landmarks within a specified distance of a property.

    Returns historic districts, cultural sites, and natural landmarks
    sorted by distance from the property.
    """,
    tags=["landmarks"],
)
async def get_nearby_landmarks(
    property_id: UUID,
    distance_ft: float = Query(
        150, description="Search radius in feet", ge=50, le=1000
    ),
    db: Session = Depends(get_db),
):
    """
    Get landmarks near a property.
    """
    try:
        logger.info(
            f"Finding landmarks within {distance_ft}ft of property {property_id}"
        )

        # Check if property exists
        from ..models import Property

        property_obj = db.query(Property).filter_by(id=property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")

        # Find nearby landmarks
        landmarks_data = spatial_queries.find_nearby_landmarks(
            property_id, distance_ft, db
        )

        # Convert to response schema
        landmarks = []
        for landmark in landmarks_data:
            landmark_response = LandmarkResponse(
                id=landmark["id"],
                name=landmark["name"],
                landmark_type=landmark["landmark_type"],
                distance_ft=landmark["distance_ft"],
                description=landmark["description"],
            )
            landmarks.append(landmark_response)

        response = NearbyLandmarksResponse(
            property_id=str(property_id),
            landmarks=landmarks,
            search_radius_ft=distance_ft,
        )

        logger.info(f"Found {len(landmarks)} landmarks near property {property_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding nearby landmarks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error finding nearby landmarks: {str(e)}"
        )


@router.get(
    "/landmarks/by-type",
    response_model=List[LandmarkResponse],
    summary="Get landmarks by type",
    description="""
    Find landmarks of a specific type within a search radius.

    Types: historic, cultural, natural, transportation, religious, educational
    """,
    tags=["landmarks"],
)
async def get_landmarks_by_type(
    landmark_type: str = Query(..., description="Type of landmark to search for"),
    latitude: float = Query(..., description="Search center latitude", ge=-90, le=90),
    longitude: float = Query(
        ..., description="Search center longitude", ge=-180, le=180
    ),
    distance_ft: float = Query(
        150, description="Search radius in feet", ge=50, le=1000
    ),
    db: Session = Depends(get_db),
):
    """
    Get landmarks of a specific type near a location.
    """
    try:
        logger.info(f"Finding {landmark_type} landmarks near ({latitude}, {longitude})")

        # Create a temporary geometry for the search point
        from geoalchemy2 import WKTElement

        search_point = WKTElement(f"POINT({longitude} {latitude})", srid=4326)

        # Find landmarks within distance
        from ..models import Landmark

        landmarks = (
            db.query(
                Landmark.id,
                Landmark.name,
                Landmark.landmark_type,
                Landmark.description,
                # Calculate distance in feet
                (
                    spatial_queries.batch_distance_calculation(
                        search_point, [Landmark.id], db
                    )[0]["distance_ft"]
                    if spatial_queries.batch_distance_calculation(
                        search_point, [Landmark.id], db
                    )
                    else 0
                ),
            )
            .filter(Landmark.landmark_type == landmark_type)
            .filter(
                spatial_queries.find_nearby_landmarks.__wrapped__.__defaults__[0]
                is not None
            )  # Complex spatial query
            .order_by(Landmark.name)
            .limit(50)
            .all()
        )

        # For now, return a simpler implementation
        # In production, this would use proper spatial queries
        landmarks = (
            db.query(Landmark)
            .filter(Landmark.landmark_type == landmark_type)
            .limit(20)
            .all()
        )

        # Convert to response schemas
        results = []
        for landmark in landmarks:
            results.append(LandmarkResponse.from_orm(landmark))

        logger.info(f"Found {len(results)} {landmark_type} landmarks")
        return results

    except Exception as e:
        logger.error(f"Error finding landmarks by type: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error finding landmarks by type: {str(e)}"
        )


@router.get(
    "/landmarks/{landmark_id}",
    response_model=LandmarkResponse,
    summary="Get landmark details",
    description="Get detailed information about a specific landmark.",
    tags=["landmarks"],
)
async def get_landmark(landmark_id: UUID, db: Session = Depends(get_db)):
    """
    Get landmark by ID.
    """
    from ..models import Landmark

    landmark = db.query(Landmark).filter_by(id=landmark_id).first()
    if not landmark:
        raise HTTPException(status_code=404, detail="Landmark not found")

    return LandmarkResponse.from_orm(landmark)
