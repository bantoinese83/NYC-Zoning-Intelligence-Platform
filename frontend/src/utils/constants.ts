/**
 * Application-wide constants and configuration.
 * Centralizes all magic numbers, strings, and configuration values.
 */

export const APP_CONFIG = {
  name: 'NYC Zoning Intelligence Platform',
  version: '0.1.0',
  description: 'Comprehensive zoning analysis and property intelligence for New York City real estate',
} as const

export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  retries: 3,
  retryDelay: 1000, // 1 second
} as const

export const MAPBOX_CONFIG = {
  accessToken: process.env.NEXT_PUBLIC_MAPBOX_TOKEN,
  defaultStyle: 'mapbox://styles/mapbox/light-v11',
  defaultCenter: [-74.0060, 40.7128] as [number, number], // NYC coordinates
  defaultZoom: 10,
  maxZoom: 18,
  minZoom: 8,
} as const

export const SEARCH_CONFIG = {
  debounceDelay: 300, // ms
  minQueryLength: 3,
  maxResults: 10,
  searchRadius: 0.001, // ~300 feet in degrees
} as const

export const PERFORMANCE_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes
  retryCount: 3,
  retryDelay: 1000,
} as const

export const ZONING_COLORS = {
  residential: '#4ade80',    // green-400
  commercial: '#f59e0b',     // amber-500
  manufacturing: '#ef4444',  // red-500
  park: '#10b981',          // emerald-500
  special: '#8b5cf6',       // violet-500
} as const

export const LANDMARK_TYPES = {
  historic: '🏛️',
  cultural: '🎭',
  natural: '🌳',
  transportation: '🚇',
  religious: '⛪',
  educational: '🎓',
} as const

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const

export const ANIMATION_CONFIG = {
  duration: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  },
} as const

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network connection failed. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Something went wrong on our end. Please try again later.',
  PERMISSION_DENIED: 'You don\'t have permission to perform this action.',
} as const

// Success messages
export const SUCCESS_MESSAGES = {
  PROPERTY_ANALYZED: 'Property analysis completed successfully.',
  REPORT_GENERATED: 'Report generated successfully.',
  SEARCH_COMPLETED: 'Search completed.',
} as const

// Loading messages
export const LOADING_MESSAGES = {
  ANALYZING_PROPERTY: 'Analyzing property zoning and regulations...',
  SEARCHING_PROPERTIES: 'Searching for properties...',
  GENERATING_REPORT: 'Generating comprehensive report...',
  LOADING_DATA: 'Loading data...',
} as const