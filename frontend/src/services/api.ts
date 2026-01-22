import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ApiResponse, ApiError } from '@/types'

class ApiClient {
  private client: AxiosInstance

  constructor(baseURL?: string) {
    this.client = axios.create({
      baseURL: `${baseURL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api`,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
      // Enable compression
      decompress: true,
      // Optimize for performance
      maxContentLength: 10 * 1024 * 1024, // 10MB max response size
      maxBodyLength: 1 * 1024 * 1024, // 1MB max request size
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add any auth headers here if needed
        // config.headers.Authorization = `Bearer ${token}`

        // Log requests in development
        if (process.env.NODE_ENV === 'development') {
          console.log('API Request:', config.method?.toUpperCase(), config.url)
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log responses in development
        if (process.env.NODE_ENV === 'development') {
          console.log('API Response:', response.status, response.config.url)
        }

        return response
      },
      (error) => {
        // Handle common errors
        if (error.response) {
          // Server responded with error status
          const status = error.response.status
          const data = error.response.data

          let message = data?.message || error.message
          let code = data?.code || 'API_ERROR'

          // Provide user-friendly messages for common HTTP status codes
          if (status === 400) {
            message = data?.message || 'Invalid request. Please check your input.'
            code = data?.code || 'BAD_REQUEST'
          } else if (status === 401) {
            message = 'Authentication required. Please log in.'
            code = 'UNAUTHORIZED'
          } else if (status === 403) {
            message = 'Access denied. You don\'t have permission to perform this action.'
            code = 'FORBIDDEN'
          } else if (status === 404) {
            message = data?.message || 'The requested resource was not found.'
            code = data?.code || 'NOT_FOUND'
          } else if (status === 422) {
            message = 'Validation error. Please check your input.'
            code = 'VALIDATION_ERROR'
          } else if (status === 429) {
            message = 'Too many requests. Please wait a moment before trying again.'
            code = 'RATE_LIMITED'
          } else if (status >= 500) {
            message = 'Server error. Please try again later.'
            code = 'SERVER_ERROR'
          }

          const apiError: ApiError = {
            message,
            code,
            details: data?.details || { status, url: error.config?.url }
          }

          // Log errors in development
          if (process.env.NODE_ENV === 'development') {
            console.error('API Error:', apiError)
          }

          return Promise.reject(apiError)
        } else if (error.request) {
          // Network error (no response received)
          const networkError: ApiError = {
            message: 'Unable to connect to the server. Please check your internet connection and try again.',
            code: 'NETWORK_ERROR',
            details: {
              originalError: error.message,
              timeout: error.config?.timeout,
              url: error.config?.url
            }
          }

          return Promise.reject(networkError)
        } else {
          // Other error
          const genericError: ApiError = {
            message: error.message || 'An unexpected error occurred',
            code: 'UNKNOWN_ERROR',
            details: { originalError: error }
          }

          return Promise.reject(genericError)
        }
      }
    )
  }

  // Generic request methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put(url, data, config)
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.patch(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete(url, config)
  }

  // Health check
  async health(): Promise<ApiResponse<any>> {
    const response = await this.get('/health')
    return response.data
  }

  // Properties
  async getProperty(id: string): Promise<ApiResponse<any>> {
    const response = await this.get(`/properties/${id}`)
    return response.data
  }

  async searchProperties(params: {
    address?: string
    city?: string
    state?: string
    limit?: number
  }): Promise<ApiResponse<any[]>> {
    const response = await this.get('/properties/search', { params })
    return response.data
  }

  async analyzeProperty(data: {
    address: string
    latitude?: number
    longitude?: number
  }): Promise<ApiResponse<any>> {
    const response = await this.post('/properties/analyze', data)
    return response.data
  }

  // Zoning
  async getZoningAnalysis(propertyId: string): Promise<ApiResponse<any>> {
    const response = await this.get(`/properties/${propertyId}/zoning`)
    return response.data
  }

  async calculateFAR(params: {
    lot_area_sf: number
    zoning_codes: string[]
    include_bonuses?: boolean
  }): Promise<ApiResponse<any>> {
    const response = await this.post('/zoning/calculate-far', params)
    return response.data
  }

  async checkCompliance(params: {
    property_id: string
    proposed_far?: number
    proposed_height?: number
  }): Promise<ApiResponse<any>> {
    const response = await this.post('/zoning/check-compliance', params)
    return response.data
  }

  // Landmarks
  async getNearbyLandmarks(params: {
    property_id: string
    distance_ft?: number
  }): Promise<ApiResponse<any>> {
    const response = await this.get('/landmarks/nearby', { params })
    return response.data
  }

  async getLandmarksByType(params: {
    type: string
    bounds?: {
      north: number
      south: number
      east: number
      west: number
    }
  }): Promise<ApiResponse<any[]>> {
    const response = await this.get('/landmarks/by-type', { params })
    return response.data
  }

  // Tax Incentives
  async checkTaxIncentives(params: {
    property_id: string
    program_codes?: string[]
  }): Promise<ApiResponse<any>> {
    const response = await this.post('/tax-incentives/check-eligibility', params)
    return response.data
  }

  async getTaxIncentivePrograms(): Promise<ApiResponse<any[]>> {
    const response = await this.get('/tax-incentives/programs')
    return response.data
  }

  // Air Rights
  async analyzeAirRights(propertyId: string): Promise<ApiResponse<any>> {
    const response = await this.get(`/air-rights/analyze/${propertyId}`)
    return response.data
  }

  async findAirRightsRecipients(propertyId: string): Promise<ApiResponse<any[]>> {
    const response = await this.get(`/air-rights/recipients/${propertyId}`)
    return response.data
  }

  // Reports
  async generateReport(params: {
    property_id: string
    include_zoning?: boolean
    include_incentives?: boolean
    include_landmarks?: boolean
    include_air_rights?: boolean
    include_valuation?: boolean
  }): Promise<Blob> {
    const response = await this.post('/reports/generate-pdf', params, {
      responseType: 'blob',
      timeout: 60000, // 60 seconds for PDF generation
    })
    return response.data
  }

  async getReportPreview(params: {
    property_id: string
    sections?: string[]
  }): Promise<ApiResponse<any>> {
    const response = await this.post('/reports/preview', params)
    return response.data
  }
}

// Create and export singleton instance
export const api = new ApiClient()

// Export class for testing or custom instances
export { ApiClient }