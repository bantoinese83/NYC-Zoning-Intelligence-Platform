export interface Landmark {
  id: string
  name: string
  landmark_type: LandmarkType
  type?: LandmarkType // For compatibility
  distance_ft: number
  distance?: number // For compatibility
  description?: string
  latitude?: number
  longitude?: number
}

export type LandmarkType =
  | 'historic'
  | 'cultural'
  | 'natural'
  | 'transportation'
  | 'religious'
  | 'educational'

export interface NearbyLandmarksResponse {
  property_id: string
  landmarks: Landmark[]
  search_radius_ft: number
}

export interface LandmarkSearchRequest {
  property_id: string
  distance_ft?: number
  landmark_type?: LandmarkType
}

export interface LandmarkFilter {
  types: LandmarkType[]
  max_distance_ft: number
  min_distance_ft?: number
}

export interface LandmarkCluster {
  id: string
  name: string
  type: LandmarkType
  count: number
  center: {
    latitude: number
    longitude: number
  }
  bounds: {
    north: number
    south: number
    east: number
    west: number
  }
}