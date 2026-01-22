'use client'

import { useQuery } from '@tanstack/react-query'
import { Property } from '@/types'
import { api } from '@/services/api'

interface SearchPropertiesParams {
  address: string
  city?: string
  state?: string
}

export function useSearchProperties(params: SearchPropertiesParams | null) {
  return useQuery({
    queryKey: ['property-search', params],
    queryFn: async (): Promise<Property[]> => {
      if (!params || !params.address || params.address.trim().length < 3) {
        return []
      }

      const queryParams = new URLSearchParams({
        address: params.address.trim(),
        ...(params.city && { city: params.city }),
        ...(params.state && { state: params.state }),
      })

      const response = await api.get(`/properties/search?${queryParams}`)

      // Ensure we return an array even if the response is malformed
      const data = Array.isArray(response.data) ? response.data : []
      return data.slice(0, 50) // Limit results to prevent memory issues
    },
    enabled: !!params && !!params.address && params.address.trim().length >= 3,
    staleTime: 5 * 60 * 1000, // 5 minutes - search results change infrequently
    gcTime: 15 * 60 * 1000, // 15 minutes - keep in cache longer
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error instanceof Error && 'status' in error && typeof error.status === 'number') {
        if (error.status >= 400 && error.status < 500) {
          return false
        }
      }
      return failureCount < 2 // Fewer retries for search
    },
    retryDelay: (attemptIndex) => Math.min(500 * 2 ** attemptIndex, 10000),
    // Add network mode for better offline handling
    networkMode: 'online',
  })
}

// Hook for debounced property search (useful for input fields)
export function useDebouncedPropertySearch(
  searchTerm: string,
  debounceMs: number = 300
) {
  return useQuery({
    queryKey: ['property-search-debounced', searchTerm],
    queryFn: async (): Promise<Property[]> => {
      if (!searchTerm || searchTerm.trim().length < 3) {
        return []
      }

      // Add delay to simulate debouncing (in practice, this would be handled by the input component)
      await new Promise(resolve => setTimeout(resolve, debounceMs))

      const response = await api.get('/properties/search', {
        params: { address: searchTerm.trim() }
      })
      return response.data
    },
    enabled: !!searchTerm && searchTerm.trim().length >= 3,
    staleTime: 1 * 60 * 1000, // 1 minute for debounced search
    gcTime: 2 * 60 * 1000,
  })
}

// Hook for getting property suggestions (autocomplete)
export function usePropertySuggestions(searchTerm: string) {
  return useQuery({
    queryKey: ['property-suggestions', searchTerm],
    queryFn: async (): Promise<string[]> => {
      if (!searchTerm || searchTerm.trim().length < 2) {
        return []
      }

      // In a real implementation, this might call a dedicated suggestions endpoint
      // For now, we'll return some mock suggestions
      const mockSuggestions = [
        `${searchTerm} Street, New York, NY`,
        `${searchTerm} Avenue, New York, NY`,
        `${searchTerm} Place, New York, NY`,
        `${searchTerm} Road, New York, NY`,
      ].filter(suggestion =>
        suggestion.toLowerCase().includes(searchTerm.toLowerCase())
      )

      return mockSuggestions.slice(0, 5)
    },
    enabled: !!searchTerm && searchTerm.trim().length >= 2,
    staleTime: 30 * 1000, // 30 seconds - suggestions can be cached briefly
    gcTime: 1 * 60 * 1000,
  })
}