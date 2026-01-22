'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { PropertySearch } from '@/components/PropertySearch'
import { PropertyMap } from '@/components/PropertyMap'
import { MapLegend } from '@/components/MapLegend'
import { ZoningResults } from '@/components/ZoningResults'
import { ReportGenerator } from '@/components/ReportGenerator'
import { PropertyCardSkeleton } from '@/components/LoadingState'
import { ErrorBoundary, ErrorFallback } from '@/components/ErrorBoundary'
import { usePropertyAnalysis } from '@/hooks/usePropertyAnalysis'
import { Property } from '@/types'
import { ArrowLeft, Building, MapPin } from 'lucide-react'
import Link from 'next/link'

export default function AnalysisPage() {
  const router = useRouter()
  const { propertyId } = router.query

  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null)

  // Fetch analysis data
  const {
    data: analysis,
    isLoading,
    error,
    refetch
  } = usePropertyAnalysis(propertyId as string)

  // Update selected property when analysis loads
  useEffect(() => {
    if (analysis?.property && !selectedProperty) {
      setSelectedProperty(analysis.property)
    }
  }, [analysis, selectedProperty])

  const handlePropertySelect = (property: Property) => {
    setSelectedProperty(property)
    // Update URL without page reload
    router.replace(`/analysis?propertyId=${property.id}`, undefined, { shallow: true })
  }

  const handleRetry = () => {
    refetch()
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Head>
          <title>
            {selectedProperty
              ? `Analysis: ${selectedProperty.address}`
              : 'Property Analysis - NYC Zoning Intelligence'
            }
          </title>
          <meta
            name="description"
            content="Detailed zoning analysis, tax incentives, and property information for NYC properties"
          />
        </Head>

        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <Link
                  href="/"
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowLeft className="h-5 w-5" />
                  <span>Back to Search</span>
                </Link>

                <div className="h-6 w-px bg-gray-300" />

                <div className="flex items-center space-x-2">
                  <Building className="h-6 w-6 text-blue-600" />
                  <span className="font-semibold text-gray-900">Property Analysis</span>
                </div>
              </div>

              {/* Property Search in Header */}
              <div className="flex-1 max-w-md">
                <PropertySearch
                  onPropertySelect={handlePropertySelect}
                  placeholder="Search another property..."
                />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {error && (
            <ErrorFallback
              error={error}
              resetError={handleRetry}
              title="Failed to load property analysis"
              message="We couldn't load the analysis for this property. Please try again."
            />
          )}

          {isLoading && !analysis && (
            <div className="space-y-6">
              <PropertyCardSkeleton />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-96 bg-gray-200 rounded-lg animate-pulse" />
                <div className="space-y-4">
                  <PropertyCardSkeleton />
                  <PropertyCardSkeleton />
                </div>
              </div>
            </div>
          )}

          {analysis && selectedProperty && (
            <div className="space-y-8">
              {/* Property Header */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                      {selectedProperty.address}
                    </h1>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-4 w-4" />
                        <span>Lot {selectedProperty.lot_number}</span>
                      </div>
                      {selectedProperty.block_number && (
                        <span>Block {selectedProperty.block_number}</span>
                      )}
                      {selectedProperty.zip_code && (
                        <span>{selectedProperty.zip_code}</span>
                      )}
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-sm text-gray-500">Land Area</div>
                    <div className="text-lg font-semibold">
                      {selectedProperty.land_area_sf?.toLocaleString()} SF
                    </div>
                  </div>
                </div>
              </div>

              {/* Map and Results Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Interactive Map */}
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <div className="p-4 border-b">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Property Location & Zoning
                    </h3>
                  </div>
                  <div className="h-96">
                    <PropertyMap analysis={analysis} showControls />
                  </div>

                  {/* Map Legend */}
                  <MapLegend />
                </div>

                {/* Analysis Summary */}
                <div className="space-y-6">
                  {/* Zoning Summary Card */}
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Zoning Summary
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-500">Base FAR</div>
                        <div className="text-xl font-bold text-blue-600">
                          {analysis.zoning.total_far_base?.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">FAR with Bonuses</div>
                        <div className="text-xl font-bold text-green-600">
                          {analysis.zoning.total_far_with_bonuses?.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">Buildable Area</div>
                        <div className="text-lg font-semibold">
                          {analysis.zoning.total_buildable_area_sf?.toLocaleString()} SF
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-500">Unused FAR</div>
                        <div className="text-lg font-semibold text-orange-600">
                          {analysis.air_rights.unused_far?.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Tax Incentives Summary */}
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Tax Incentives
                    </h3>
                    <div className="space-y-3">
                      {analysis.tax_incentives.slice(0, 3).map((incentive, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm font-medium">{incentive.program_name}</span>
                          <span className={`text-sm font-medium ${
                            incentive.is_eligible ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {incentive.is_eligible ? 'Eligible' : 'Not Eligible'}
                          </span>
                        </div>
                      ))}
                      {analysis.tax_incentives.length > 3 && (
                        <div className="text-sm text-gray-500 text-center">
                          +{analysis.tax_incentives.length - 3} more programs
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Landmarks Summary */}
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Nearby Landmarks
                    </h3>
                    <div className="space-y-2">
                      {analysis.nearby_landmarks.slice(0, 3).map((landmark, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm">{landmark.name}</span>
                          <span className="text-sm text-gray-500">
                            {landmark.distance_ft} ft
                          </span>
                        </div>
                      ))}
                      {analysis.nearby_landmarks.length > 3 && (
                        <div className="text-sm text-gray-500 text-center">
                          +{analysis.nearby_landmarks.length - 3} more landmarks
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed Results */}
              <ZoningResults analysis={analysis} />

              {/* Report Generator */}
              <ReportGenerator
                propertyId={selectedProperty.id}
                analysis={analysis}
              />
            </div>
          )}
        </main>
      </div>
    </ErrorBoundary>
  )
}