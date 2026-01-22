import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'

export interface PlatformStats {
  properties_analyzed: number
  tax_programs: number
  zoning_districts: number
  landmarks: number
  data_accuracy: number
  last_updated: string | null
  error?: string
}

export function useStats() {
  return useQuery<PlatformStats>({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await api.get('/stats')
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error && 'status' in error && typeof error.status === 'number' && error.status >= 400 && error.status < 500) {
        return false
      }
      return failureCount < 2
    },
    // Refetch every 10 minutes
    refetchInterval: 10 * 60 * 1000,
    refetchIntervalInBackground: true,
  })
}