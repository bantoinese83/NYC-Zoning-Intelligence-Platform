'use client'

import { useQuery } from '@tanstack/react-query'
import { PropertyAnalysis } from '@/types'
import { api } from '@/services/api'

export function usePropertyAnalysis(propertyId: string | undefined) {
  return useQuery({
    queryKey: ['property-analysis', propertyId],
    queryFn: async (): Promise<PropertyAnalysis> => {
      if (!propertyId) {
        throw new Error('Property ID is required')
      }

      const response = await api.get(`/properties/${propertyId}/analysis`)
      return response.data
    },
    enabled: !!propertyId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error instanceof Error && 'status' in error && typeof error.status === 'number') {
        if (error.status >= 400 && error.status < 500) {
          return false
        }
      }
      // Retry up to 3 times for other errors
      return failureCount < 3
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}

// Hook for getting basic property info
export function useProperty(propertyId: string | undefined) {
  return useQuery({
    queryKey: ['property', propertyId],
    queryFn: async () => {
      if (!propertyId) {
        throw new Error('Property ID is required')
      }

      const response = await api.get(`/properties/${propertyId}`)
      return response.data
    },
    enabled: !!propertyId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Hook for property zoning analysis only
export function usePropertyZoning(propertyId: string | undefined) {
  return useQuery({
    queryKey: ['property-zoning', propertyId],
    queryFn: async () => {
      if (!propertyId) {
        throw new Error('Property ID is required')
      }

      const response = await api.get(`/properties/${propertyId}/zoning`)
      return response.data
    },
    enabled: !!propertyId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}