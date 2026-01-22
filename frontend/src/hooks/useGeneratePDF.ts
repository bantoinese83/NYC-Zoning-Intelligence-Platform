'use client'

import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'

interface PDFReportRequest {
  property_id: string
  include_zoning?: boolean
  include_incentives?: boolean
  include_landmarks?: boolean
  include_air_rights?: boolean
  include_valuation?: boolean
}

export function useGeneratePDF() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (params: PDFReportRequest): Promise<Blob> => {
      const response = await api.post('/reports/generate-pdf', params, {
        responseType: 'blob', // Important for handling binary data
        timeout: 60000, // 60 seconds timeout for PDF generation
      })

      // Return the blob directly
      return response.data
    },
    onSuccess: (data, variables) => {
      // Create download link
      const url = window.URL.createObjectURL(data)
      const link = document.createElement('a')
      link.href = url
      link.download = `zoning-report-${variables.property_id}.pdf`
      document.body.appendChild(link)
      link.click()

      // Cleanup
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({
        queryKey: ['property-analysis', variables.property_id]
      })
    },
    onError: (error) => {
      console.error('PDF generation failed:', error)
      // Error handling is done in the component
    },
    retry: false, // Don't retry PDF generation failures
  })
}

// Hook for PDF preview (data only, no download)
export function usePDFPreview() {
  return useMutation({
    mutationFn: async (params: Omit<PDFReportRequest, 'include_valuation'> & {
      sections?: string[]
    }) => {
      const response = await api.post('/reports/preview', params)
      return response.data
    },
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error instanceof Error && 'status' in error && typeof error.status === 'number') {
        if (error.status >= 400 && error.status < 500) {
          return false
        }
      }
      return failureCount < 2
    },
  })
}

// Hook for getting PDF templates
export function usePDFTemplates() {
  return useMutation({
    mutationFn: async () => {
      const response = await api.get('/reports/templates')
      return response.data
    },
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error instanceof Error && 'status' in error && typeof error.status === 'number') {
        if (error.status >= 400 && error.status < 500) {
          return false
        }
      }
      return failureCount < 2
    },
  })
}

// Utility function to validate PDF options
export function validatePDFOptions(options: Partial<PDFReportRequest>): {
  isValid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (!options.property_id) {
    errors.push('Property ID is required')
  }

  const sections = [
    options.include_zoning,
    options.include_incentives,
    options.include_landmarks,
    options.include_air_rights,
    options.include_valuation
  ]

  if (!sections.some(section => section !== false)) {
    errors.push('At least one report section must be selected')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

// Hook for tracking PDF generation progress (if implemented on backend)
export function usePDFGenerationProgress(generationId?: string) {
  return useQuery({
    queryKey: ['pdf-progress', generationId],
    queryFn: async () => {
      if (!generationId) return null

      const response = await api.get(`/reports/progress/${generationId}`)
      return response.data
    },
    enabled: !!generationId,
    refetchInterval: (data) => {
      // Stop polling when complete or failed
      if (data && 'status' in data && (data.status === 'completed' || data.status === 'failed')) {
        return false
      }
      return 2000 // Poll every 2 seconds
    },
    staleTime: 1000, // Always fresh for progress
  })
}