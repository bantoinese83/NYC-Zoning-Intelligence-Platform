'use client'

import { useMutation } from '@tanstack/react-query'
import { PropertyData, AnalysisResult, AILandmark } from '@/types'
import { searchProperty, performDeepAnalysis, findNearbyLandmarks } from '@/services/geminiAI'

/**
 * Hook for AI-powered property search
 */
export function useAISearchProperty() {
  return useMutation({
    mutationFn: async (address: string): Promise<PropertyData> => {
      return await searchProperty(address)
    },
    onError: (error) => {
      console.error('AI Property Search Error:', error)
    }
  })
}

/**
 * Hook for AI-powered deep property analysis
 */
export function useAIDeepAnalysis() {
  return useMutation({
    mutationFn: async (property: PropertyData): Promise<AnalysisResult> => {
      return await performDeepAnalysis(property)
    },
    onError: (error) => {
      console.error('AI Deep Analysis Error:', error)
    }
  })
}

/**
 * Hook for finding nearby landmarks using AI
 */
export function useAINearbyLandmarks() {
  return useMutation({
    mutationFn: async ({ lat, lng }: { lat: number; lng: number }): Promise<AILandmark[]> => {
      return await findNearbyLandmarks(lat, lng)
    },
    onError: (error) => {
      console.warn('AI Nearby Landmarks Error:', error)
    }
  })
}

/**
 * Combined hook for complete AI-powered property analysis
 */
export function useAIPropertyAnalysis(address: string | null) {
  // Step 1: Search for property
  const searchMutation = useAISearchProperty()

  // Step 2: Perform deep analysis (depends on search result)
  const analysisMutation = useAIDeepAnalysis()

  // Step 3: Find nearby landmarks (depends on property coordinates)
  const landmarksMutation = useAINearbyLandmarks()

  // Chain the operations
  const performFullAnalysis = async () => {
    if (!address) return null

    try {
      // Step 1: Search
      const propertyData = await searchMutation.mutateAsync(address)

      // Step 2: Deep analysis
      const analysisResult = await analysisMutation.mutateAsync(propertyData)

      // Step 3: Find landmarks
      const landmarks = await landmarksMutation.mutateAsync({
        lat: propertyData.coordinates.lat,
        lng: propertyData.coordinates.lng
      })

      // Combine results
      return {
        ...analysisResult,
        nearby_landmarks: landmarks
      }
    } catch (error) {
      console.error('AI Analysis Chain Error:', error)
      throw error
    }
  }

  return {
    // Individual mutations for granular control
    searchProperty: searchMutation,
    performAnalysis: analysisMutation,
    findLandmarks: landmarksMutation,

    // Combined operation
    performFullAnalysis,

    // Loading states
    isLoading: searchMutation.isPending || analysisMutation.isPending || landmarksMutation.isPending,

    // Error states
    error: searchMutation.error || analysisMutation.error || landmarksMutation.error,

    // Data
    propertyData: searchMutation.data,
    analysisData: analysisMutation.data,
    landmarksData: landmarksMutation.data
  }
}