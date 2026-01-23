/**
 * Testing utilities for React components and hooks.
 * Provides common test helpers, mocks, and utilities.
 */

import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock implementations for common dependencies
export const mockMapbox = {
  Map: jest.fn().mockImplementation(() => ({
    on: jest.fn(),
    off: jest.fn(),
    addControl: jest.fn(),
    removeControl: jest.fn(),
    addSource: jest.fn(),
    removeSource: jest.fn(),
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
    getSource: jest.fn(),
    getLayer: jest.fn(),
    getStyle: jest.fn(() => ({ layers: [] })),
    setStyle: jest.fn(),
    flyTo: jest.fn(),
    easeTo: jest.fn(),
    fitBounds: jest.fn(),
    resize: jest.fn(),
    remove: jest.fn(),
    isStyleLoaded: jest.fn(() => true),
  })),
  NavigationControl: jest.fn(),
  ScaleControl: jest.fn(),
  Popup: jest.fn().mockImplementation(() => ({
    setLngLat: jest.fn().mockReturnThis(),
    setHTML: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn(),
  })),
}

// Custom render function with providers
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export { customRender as render }

// Test data factories
export const createMockProperty = (overrides = {}) => ({
  id: 'test-property-1',
  address: '123 Main St, New York, NY 10001',
  lot_number: '0123',
  block_number: '0123',
  zip_code: '10001',
  building_area_sf: 5000,
  land_area_sf: 2500,
  current_use: 'Residential',
  latitude: 40.7128,
  longitude: -74.0060,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

export const createMockZoningAnalysis = (overrides = {}) => ({
  property_id: 'test-property-1',
  zoning_districts: [
    {
      code: 'R10',
      name: 'Residential 10',
      far_base: 10.0,
      far_with_bonus: 12.0,
      max_height_ft: 150,
    },
  ],
  far_analysis: {
    far_effective: 8.5,
    far_max: 10.0,
    far_utilized: 85.0,
  },
  district_count: 1,
  ...overrides,
})

export const createMockTaxIncentive = (overrides = {}) => ({
  program_name: '467-M Residential Conversion',
  program_code: '467-M',
  description: 'Tax abatement for converting commercial to residential',
  is_eligible: true,
  eligibility_reason: 'Property meets all 467-M requirements',
  estimated_abatement_value: 50000,
  ...overrides,
})

export const createMockLandmark = (overrides = {}) => ({
  id: 'landmark-1',
  name: 'Empire State Building',
  landmark_type: 'cultural',
  type: 'cultural',
  distance_ft: 5280, // 1 mile
  distance: 5280,
  latitude: 40.7484,
  longitude: -73.9857,
  description: 'Iconic Art Deco skyscraper',
  ...overrides,
})

// Mock API responses
export const mockApiResponses = {
  propertySearch: {
    data: [createMockProperty()],
    status: 'success',
  },
  zoningAnalysis: {
    data: createMockZoningAnalysis(),
    status: 'success',
  },
  taxIncentives: {
    data: [createMockTaxIncentive()],
    status: 'success',
  },
  landmarks: {
    data: [createMockLandmark()],
    status: 'success',
  },
  stats: {
    data: {
      properties_analyzed: 500,
      tax_programs: 15,
      zoning_districts: 97,
      landmarks: 52,
      data_accuracy: 100,
    },
    status: 'success',
  },
}

// Utility functions for tests
export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0))

export const createMockEvent = (type: string, overrides = {}) => ({
  type,
  preventDefault: jest.fn(),
  stopPropagation: jest.fn(),
  target: {
    value: '',
    checked: false,
    ...overrides,
  },
  ...overrides,
})

export const mockConsoleError = () => {
  const originalError = console.error
  beforeAll(() => {
    console.error = jest.fn()
  })
  afterAll(() => {
    console.error = originalError
  })
}

export const mockConsoleWarn = () => {
  const originalWarn = console.warn
  beforeAll(() => {
    console.warn = jest.fn()
  })
  afterAll(() => {
    console.warn = originalWarn
  })
}

// Performance testing utilities
export const measureRenderTime = async (
  component: ReactElement,
  iterations = 10
) => {
  const times: number[] = []

  for (let i = 0; i < iterations; i++) {
    const start = performance.now()
    customRender(component)
    const end = performance.now()
    times.push(end - start)
  }

  return {
    average: times.reduce((a, b) => a + b, 0) / times.length,
    min: Math.min(...times),
    max: Math.max(...times),
    median: times.sort((a, b) => a - b)[Math.floor(times.length / 2)],
  }
}

// Accessibility testing helpers
export const checkAccessibility = (container: HTMLElement) => {
  const issues: string[] = []

  // Check for alt text on images
  const images = container.querySelectorAll('img')
  images.forEach((img, index) => {
    if (!img.alt && !img.getAttribute('aria-label')) {
      issues.push(`Image ${index} missing alt text`)
    }
  })

  // Check for labels on form inputs
  const inputs = container.querySelectorAll('input, select, textarea')
  inputs.forEach((input, index) => {
    const label = container.querySelector(`label[for="${input.id}"]`)
    if (!label && !input.getAttribute('aria-label')) {
      issues.push(`Input ${index} missing label`)
    }
  })

  // Check for sufficient color contrast (simplified)
  const textElements = container.querySelectorAll('*')
  textElements.forEach((element) => {
    const style = window.getComputedStyle(element)
    if (style.color && style.backgroundColor) {
      // This is a simplified check - in real tests you'd use a proper color contrast library
      if (style.color === style.backgroundColor) {
        issues.push(`Element has same text and background color`)
      }
    }
  })

  return issues
}

// Mock router for Next.js
export const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  pathname: '/',
  query: {},
  asPath: '/',
  events: {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
  },
}

// Local storage mock
export const mockLocalStorage = () => {
  const store: Record<string, string> = {}

  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: jest.fn((key: string) => store[key] || null),
      setItem: jest.fn((key: string, value: string) => {
        store[key] = value
      }),
      removeItem: jest.fn((key: string) => {
        delete store[key]
      }),
      clear: jest.fn(() => {
        Object.keys(store).forEach(key => delete store[key])
      }),
      key: jest.fn((index: number) => Object.keys(store)[index] || null),
      get length() {
        return Object.keys(store).length
      },
    },
    writable: true,
  })
}

// Intersection Observer mock
export const mockIntersectionObserver = () => {
  global.IntersectionObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }))
}

// Resize Observer mock
export const mockResizeObserver = () => {
  global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }))
}

// Setup all mocks at once
export const setupTestEnvironment = () => {
  mockLocalStorage()
  mockIntersectionObserver()
  mockResizeObserver()

  // Mock mapbox
  jest.mock('mapbox-gl', () => mockMapbox)

  // Mock next/router
  jest.mock('next/router', () => ({
    useRouter: () => mockRouter,
  }))
}