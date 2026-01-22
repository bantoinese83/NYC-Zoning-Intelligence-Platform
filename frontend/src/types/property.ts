export interface Property {
  id: string
  address: string
  lot_number: string
  block_number?: string
  zip_code: string
  building_area_sf?: number
  land_area_sf: number
  current_use?: string
  latitude?: number
  longitude?: number
  created_at: string
  updated_at: string
}

export interface PropertyCreate extends Pick<Property, 'address'> {
  city?: string
  state?: string
  latitude?: number
  longitude?: number
}

export type PropertyResponse = Property

export interface AddressSearchRequest {
  address: string
  city?: string
  state?: string
}

export interface PropertySearchResult {
  properties: Property[]
  total: number
  query: string
}

// Gemini AI Integration Types
export interface PropertyData {
  address: string
  borough: string
  zoningDistrict: string
  lotArea: number
  buildingClass: string
  yearBuilt: number
  coordinates: {
    lat: number
    lng: number
  }
  details: string
}

export interface AIZoningAnalysis {
  maxFar?: number
  allowedFar?: number
  usedFar?: number
  availableAirRights?: number
  airRightsMarketValue?: number
  developmentPotential?: string
  zoningCode?: string
  summary?: string
}

export interface TaxIncentive {
  programName?: string // For AI responses
  program_name?: string // For compatibility with existing code
  description: string
  eligibilityProbability?: 'High' | 'Medium' | 'Low'
  eligibility_probability?: 'High' | 'Medium' | 'Low' // For compatibility
  estimatedSavings?: string
  estimated_savings?: string // For compatibility
  is_eligible?: boolean
  eligibility_reason?: string
  estimated_abatement_value?: number
}

export interface AILandmark {
  name: string
  type?: string // For AI responses
  distance?: string
  latitude?: number
  longitude?: number
  coordinates?: {
    lat: number
    lng: number
  }
  description?: string
  address?: string
}

export interface AnalysisResult {
  property: PropertyData
  zoning: AIZoningAnalysis
  incentives: TaxIncentive[]
  sources: Array<{ title: string; uri: string }>
}

// Import existing ZoningAnalysis from zoning types
import { ZoningAnalysis } from './zoning'

export interface PropertyAnalysis {
  property: Property
  zoning: ZoningAnalysis
  tax_incentives: TaxIncentive[]
  nearby_landmarks: AILandmark[]
  air_rights: any // AirRights
  report_data?: Record<string, any>
}