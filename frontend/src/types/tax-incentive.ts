export interface TaxIncentiveProgram {
  id: string
  program_code: string
  program_name: string
  description?: string
  eligible_zoning_districts: string[]
  min_building_age?: number
  requires_residential: boolean
  tax_abatement_years: number
  created_at: string
}

export interface PropertyTaxIncentive {
  id: string
  program_code: string
  program_name: string
  is_eligible: boolean
  eligibility_reason: string
  estimated_abatement_value?: number
  details?: TaxIncentiveDetails
}

export interface TaxIncentiveDetails {
  program_code: string
  program_name: string
  description: string
  eligibility_criteria: string[]
  benefits: string[]
  application_process: string[]
  estimated_savings: {
    annual: number
    total: number
    years: number
  }
  requirements: string[]
}

export interface TaxIncentiveEligibilityRequest {
  property_id: string
  program_codes?: string[]
}

export interface TaxIncentiveEligibilityResponse {
  property_id: string
  incentives: PropertyTaxIncentive[]
  total_estimated_savings?: number
}

export interface TaxIncentiveSummary {
  total_eligible_programs: number
  total_estimated_value: number
  top_programs: PropertyTaxIncentive[]
  eligibility_breakdown: {
    eligible: number
    ineligible: number
    unknown: number
  }
}