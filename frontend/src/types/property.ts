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

export interface TaxIncentive {
  program_name: string
  description: string
  is_eligible: boolean
  eligibility_reason: string
  estimated_abatement_value: number
}

// Import Landmark from landmark types to avoid conflicts
import { Landmark } from './landmark'

export interface PropertyAnalysis {
  property: Property
  zoning: any // ZoningAnalysis - will be imported from zoning types
  tax_incentives: TaxIncentive[]
  nearby_landmarks: Landmark[]
  air_rights: any // AirRights
  report_data?: Record<string, any>
}