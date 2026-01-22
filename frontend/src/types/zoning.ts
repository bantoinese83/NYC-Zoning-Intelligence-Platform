export interface ZoningDistrict {
  id: string
  district_code: string
  district_name?: string
  far_base: number
  far_with_bonus: number
  max_height_ft?: number
  setback_requirements: {
    front_ft: number
    side_ft: number
    rear_ft: number
  }
  building_class?: string
  created_at: string
}

export interface PropertyZoning {
  property_id: string
  district_code: string
  district_name?: string
  percent_in_district: number
  far_base: number
  far_with_bonus: number
  max_height_ft?: number
  setback_requirements: {
    front_ft: number
    side_ft: number
    rear_ft: number
  }
}

export interface ZoningAnalysis {
  property: any // PropertyResponse
  zoning_districts: PropertyZoning[]
  total_buildable_area_sf: number
  max_height_ft?: number
  air_rights_available: boolean
}

export interface FARCalculatorRequest {
  lot_area_sf: number
  zoning_codes: string[]
  include_bonuses?: boolean
}

export interface FARCalculatorResponse {
  far: number
  buildable_sf: number
  with_bonuses?: number
}

export interface ZoningComplianceRequest {
  property_id: string
  proposed_far?: number
  proposed_height?: number
}

export interface ZoningComplianceResponse {
  compliant: boolean
  violations: string[]
  max_far: number
  max_height_ft?: number
}

export interface SetbackRequirements {
  front_ft: number
  side_ft: number
  rear_ft: number
}