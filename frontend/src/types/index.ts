// Re-export all types for easy importing
export * from './property'
export * from './zoning'
export * from './landmark'
export * from './tax-incentive'
export * from './air-rights'
export * from './api'
export * from './common'

// Global type utilities
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = Pick<T, Exclude<keyof T, Keys>> & {
  [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Keys>>
}[Keys]

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// API Response wrapper
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
}

// Pagination types
export interface PaginationMeta {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: PaginationMeta
}

// Error types
export interface ApiError {
  message: string
  code: string
  details?: Record<string, any>
}

// Loading states
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

// Form states
export interface FormState<T = any> {
  data: T
  errors: Record<string, string>
  isSubmitting: boolean
  isValid: boolean
}

// Map types
export interface MapViewport {
  latitude: number
  longitude: number
  zoom: number
  bearing?: number
  pitch?: number
}

export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}