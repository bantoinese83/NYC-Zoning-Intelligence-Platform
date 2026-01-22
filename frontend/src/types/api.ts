import { Property, PropertyAnalysis } from './property'
import { ZoningAnalysis, FARCalculatorRequest, ZoningComplianceRequest } from './zoning'
import { NearbyLandmarksResponse, LandmarkSearchRequest } from './landmark'
import { TaxIncentiveEligibilityResponse } from './tax-incentive'
import { AirRights } from './air-rights'

// API Response types
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
  status: 'success' | 'error'
}

export interface PaginatedApiResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Property API
export interface PropertyApi {
  analyze: (data: {
    address: string
    latitude?: number
    longitude?: number
  }) => Promise<ApiResponse<PropertyAnalysis>>

  getById: (id: string) => Promise<ApiResponse<Property>>

  search: (params: {
    address: string
    city?: string
    state?: string
  }) => Promise<ApiResponse<Property[]>>

  getAnalysis: (id: string) => Promise<ApiResponse<PropertyAnalysis>>
}

// Zoning API
export interface ZoningApi {
  getAnalysis: (propertyId: string) => Promise<ApiResponse<ZoningAnalysis>>

  getDistrict: (code: string) => Promise<ApiResponse<any>>

  calculateFAR: (params: FARCalculatorRequest) => Promise<ApiResponse<any>>

  checkCompliance: (params: ZoningComplianceRequest) => Promise<ApiResponse<any>>

  getSetbacks: (propertyId: string) => Promise<ApiResponse<any>>
}

// Landmark API
export interface LandmarkApi {
  getNearby: (params: {
    property_id: string
    distance_ft?: number
  }) => Promise<ApiResponse<NearbyLandmarksResponse>>

  getByType: (params: LandmarkSearchRequest) => Promise<ApiResponse<any[]>>

  getById: (id: string) => Promise<ApiResponse<any>>
}

// Tax Incentive API
export interface TaxIncentiveApi {
  checkEligibility: (params: {
    property_id: string
    program_codes?: string[]
  }) => Promise<ApiResponse<TaxIncentiveEligibilityResponse>>

  getProgramDetails: (params: {
    property_id: string
    program_code: string
  }) => Promise<ApiResponse<any>>

  listPrograms: () => Promise<ApiResponse<any[]>>
}

// Air Rights API
export interface AirRightsApi {
  analyze: (propertyId: string) => Promise<ApiResponse<AirRights>>

  getRecipients: (propertyId: string) => Promise<ApiResponse<any>>

  simulateTransfer: (params: {
    from_property_id: string
    to_property_id: string
    far_to_transfer: number
  }) => Promise<ApiResponse<any>>

  getMarketData: () => Promise<ApiResponse<any>>
}

// Reports API
export interface ReportsApi {
  generatePDF: (params: {
    property_id: string
    include_zoning?: boolean
    include_incentives?: boolean
    include_landmarks?: boolean
    include_air_rights?: boolean
  }) => Promise<Blob>

  previewReport: (params: {
    property_id: string
    sections?: string[]
  }) => Promise<ApiResponse<PropertyAnalysis>>

  getTemplates: () => Promise<ApiResponse<any[]>>
}

// Main API interface
export interface ApiClient {
  properties: PropertyApi
  zoning: ZoningApi
  landmarks: LandmarkApi
  taxIncentives: TaxIncentiveApi
  airRights: AirRightsApi
  reports: ReportsApi
  health: () => Promise<ApiResponse<any>>
}

// HTTP Client configuration
export interface HttpClientConfig {
  baseURL: string
  timeout?: number
  headers?: Record<string, string>
  retries?: number
}

// Request/Response interceptors
export interface RequestInterceptor {
  (config: any): any
}

export interface ResponseInterceptor {
  (response: any): any
  (error: any): Promise<any>
}

// Error types
export interface ApiError {
  message: string
  code: string
  statusCode?: number
  details?: Record<string, any>
}

export class ApiException extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: Record<string, any>
  ) {
    super(message)
    this.name = 'ApiException'
  }
}