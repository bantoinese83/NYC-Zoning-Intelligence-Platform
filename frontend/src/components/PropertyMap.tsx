'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import { Loader2, Layers, ZoomIn, ZoomOut, Locate, AlertTriangle } from 'lucide-react'
import { PropertyAnalysis, MapViewport, Property } from '@/types'
import { Button } from './ui/Button'
import { api } from '@/services/api'

interface PropertyMapProps {
  analysis?: PropertyAnalysis
  className?: string
  onViewportChange?: (viewport: MapViewport) => void
  showControls?: boolean
}

// Helper functions for zoning and landmark information
const getZoningTypeDescription = (code?: string): string => {
  if (!code) return 'Unknown'

  if (code.startsWith('R')) return 'Residential'
  if (code.startsWith('C')) return 'Commercial'
  if (code.startsWith('M')) return 'Manufacturing'
  if (code.startsWith('P')) return 'Park'
  return 'Special Purpose'
}

const getZoningDescription = (code?: string): string => {
  if (!code) return 'Zoning district information not available'

  const descriptions: Record<string, string> = {
    'R10': 'High-density residential district',
    'R8': 'Medium-high density residential district',
    'R6': 'Medium-density residential district',
    'C6-4': 'Commercial district with residential overlay',
    'C4': 'Local commercial district',
    'C2': 'Neighborhood commercial district',
    'M1-1': 'Light manufacturing district',
    'M2': 'Medium manufacturing district',
    'M3': 'Heavy manufacturing district'
  }

  return descriptions[code] || 'General zoning district for mixed use'
}

const getLandmarkCategory = (type?: string): string => {
  const categories: Record<string, string> = {
    'historic': 'Historical landmark or building',
    'cultural': 'Cultural institution or venue',
    'natural': 'Park, garden, or natural feature',
    'transportation': 'Transportation hub or facility',
    'religious': 'Religious or spiritual site',
    'educational': 'School or educational facility'
  }

  return categories[type || ''] || 'Point of interest'
}

const getLandmarkIcon = (type?: string): string => {
  const icons: Record<string, string> = {
    'historic': '🏰',
    'cultural': '🎭',
    'natural': '🌳',
    'transportation': '🚇',
    'religious': '⛪',
    'educational': '🏫'
  }

  return icons[type || ''] || '📍'
}

export function PropertyMap({
  analysis,
  className = "",
  onViewportChange,
  showControls = true
}: PropertyMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const viewportTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [mapError, setMapError] = useState<string | null>(null)
  const [layers, setLayers] = useState({
    zoning: true,
    landmarks: true,
    property: true
  })
  const [generalProperties, setGeneralProperties] = useState<Property[]>([])
  const [propertiesLoaded, setPropertiesLoaded] = useState(false)
  const [mapLoaded, setMapLoaded] = useState(false)

  // Debounced viewport change handler for performance
  const debouncedViewportChange = useCallback((viewport: any) => {
    if (viewportTimeoutRef.current) {
      clearTimeout(viewportTimeoutRef.current)
    }

    viewportTimeoutRef.current = setTimeout(() => {
      onViewportChange?.(viewport)
    }, 150) // Debounce for 150ms
  }, [onViewportChange])

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return

    const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN
    if (!mapboxToken) {
      console.error('Mapbox token not configured')
      setMapError('Mapbox token not configured. Please check your environment variables.')
      setIsLoading(false)
      return
    }

    mapboxgl.accessToken = mapboxToken

    // Ensure the container is empty before initializing the map
    // Mapbox GL JS requires the container to be empty for proper initialization
    if (mapContainer.current) {
      mapContainer.current.innerHTML = ''
    }

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [-74.0060, 40.7128], // NYC center
      zoom: 12,
      pitch: 0,
      bearing: 0,
      // Enhanced map options for better performance and UX
      minZoom: 10,
      maxZoom: 18,
      maxBounds: [
        [-74.3, 40.4], // Southwest coordinates
        [-73.7, 40.9]  // Northeast coordinates (NYC bounds)
      ],
      // Enable cooperative gestures for better mobile experience
      cooperativeGestures: true,
      // Improve performance
      preserveDrawingBuffer: false,
      // Better rendering quality
      antialias: true
    })

    map.current.on('load', () => {
      setIsLoading(false)
      setMapError(null)
      setMapLoaded(true)
    })

    map.current.on('error', (e) => {
      console.error('Map failed to load:', e)
      setMapError('Failed to load map. Please check your internet connection and try again.')
      setIsLoading(false)
    })

    map.current.on('style.load', () => {
      // Style loaded successfully, clear any previous errors
      setMapError(null)
    })

    map.current.on('moveend', () => {
      if (onViewportChange && map.current) {
        const center = map.current.getCenter()
        const zoom = map.current.getZoom()
        debouncedViewportChange({
          latitude: center.lat,
          longitude: center.lng,
          zoom,
          bearing: map.current.getBearing(),
          pitch: map.current.getPitch()
        })
      }
    })

    return () => {
      // Clear any pending viewport updates
      if (viewportTimeoutRef.current) {
        clearTimeout(viewportTimeoutRef.current)
        viewportTimeoutRef.current = null
      }

      if (map.current) {
        try {
          // Remove all event listeners - Mapbox GL JS off() without args removes all listeners
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          ;(map.current as any).off()

          // Remove all layers and sources safely
          // Only attempt cleanup if map is still in a valid state
          try {
            // Check if map is loaded and has a valid style before accessing it
            if (map.current.isStyleLoaded && map.current.isStyleLoaded()) {
              const style = map.current.getStyle()
              if (style && typeof style === 'object' && style.layers && style.sources) {
                const layers = style.layers || []
                layers.forEach(layer => {
                  try {
                    if (map.current?.getLayer && typeof map.current.getLayer === 'function' && map.current.getLayer(layer.id)) {
                      map.current.removeLayer(layer.id)
                    }
                  } catch (layerError) {
                    // Silently ignore layer removal errors
                    console.warn('Error removing layer:', layer.id, layerError)
                  }
                })

                const sources = Object.keys(style.sources || {})
                sources.forEach(source => {
                  try {
                    if (map.current?.getSource && typeof map.current.getSource === 'function' && map.current.getSource(source)) {
                      map.current.removeSource(source)
                    }
                  } catch (sourceError) {
                    // Silently ignore source removal errors
                    console.warn('Error removing source:', source, sourceError)
                  }
                })
              }
            }
          } catch (styleError) {
            // Silently ignore style access errors during cleanup
            // This is expected when map is being destroyed
            console.debug('Map style cleanup skipped during destruction:', styleError instanceof Error ? styleError.message : String(styleError))
          }

          // Remove the map
          map.current.remove()
        } catch (cleanupError) {
          // Silently ignore cleanup errors
          console.warn('Error during map cleanup:', cleanupError)
        } finally {
          map.current = null
        }
      }
    }
  }, [debouncedViewportChange]) // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch general properties for overview map (when no specific analysis)
  useEffect(() => {
    if (analysis || propertiesLoaded) return

    const fetchGeneralProperties = async () => {
      try {
        // Fetch a sample of properties for the overview map
        const response = await api.get('/properties/search', {
          params: {
            address: 'Manhattan, NY', // Get properties from Manhattan as a sample
            limit: 50 // Limit to avoid cluttering the map
          }
        })

        if (response.data && Array.isArray(response.data)) {
          setGeneralProperties(response.data)
        }
        setPropertiesLoaded(true)
      } catch (error) {
        console.warn('Failed to fetch general properties for map overview:', error)
        setPropertiesLoaded(true) // Mark as loaded even on error
      }
    }

    fetchGeneralProperties()
  }, [analysis, propertiesLoaded])

  // Add popup functionality
  useEffect(() => {
    if (!map.current) return

    const mapInstance = map.current
    const popup = new mapboxgl.Popup({
      closeButton: true,
      closeOnClick: true,
      className: 'custom-popup'
    })

    // Add click handlers for zoning districts
    mapInstance.on('click', 'zoning-fill', (e) => {
      if (e.features && e.features[0]) {
        const feature = e.features[0]
        const properties = feature.properties

        popup.setLngLat(e.lngLat)
          .setHTML(`
            <div class="p-3 max-w-xs">
              <h3 class="font-bold text-lg text-gray-900 mb-2">${properties?.code || 'Unknown District'}</h3>
              <div class="space-y-1 text-sm">
                <p><span class="font-medium">Type:</span> ${getZoningTypeDescription(properties?.code)}</p>
                <p><span class="font-medium">FAR:</span> ${properties?.far ? properties.far.toFixed(2) : 'N/A'}</p>
                <p><span class="font-medium">Description:</span> ${getZoningDescription(properties?.code)}</p>
              </div>
            </div>
          `)
          .addTo(mapInstance)
      }
    })

    // Add click handlers for landmarks
    mapInstance.on('click', 'landmarks', (e) => {
      if (e.features && e.features[0]) {
        const feature = e.features[0]
        const properties = feature.properties

        popup.setLngLat(e.lngLat)
          .setHTML(`
            <div class="p-4 max-w-sm">
              <div class="flex items-start space-x-3 mb-3">
                <div class="flex-shrink-0">
                  ${getLandmarkIcon(properties?.type)}
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="font-bold text-lg text-gray-900 mb-1">${properties?.name || 'Landmark'}</h3>
                  <p class="text-sm text-gray-600 capitalize">${properties?.type || 'Unknown'} Landmark</p>
                </div>
              </div>
              <div class="space-y-2 text-sm border-t border-gray-200 pt-3">
                ${properties?.description ? `<p class="text-gray-700">${properties.description}</p>` : ''}
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Distance:</span>
                  <span class="font-semibold text-gray-900">${properties?.distance ? `${properties.distance} ft` : 'Unknown'}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600">Category:</span>
                  <span class="font-semibold text-gray-900">${getLandmarkCategory(properties?.type)}</span>
                </div>
              </div>
            </div>
          `)
          .addTo(mapInstance)
      }
    })

    // Change cursor on hover
    mapInstance.on('mouseenter', 'zoning-fill', () => {
      mapInstance.getCanvas().style.cursor = 'pointer'
    })

    mapInstance.on('mouseleave', 'zoning-fill', () => {
      mapInstance.getCanvas().style.cursor = ''
    })

    mapInstance.on('mouseenter', 'landmarks', () => {
      mapInstance.getCanvas().style.cursor = 'pointer'
    })

    mapInstance.on('mouseleave', 'landmarks', () => {
      mapInstance.getCanvas().style.cursor = ''
    })

    // Add click handlers for general properties
    mapInstance.on('click', 'general-properties', (e) => {
      if (e.features && e.features[0]) {
        const feature = e.features[0]
        const properties = feature.properties

        const address = properties?.address || 'Property'
        const currentUse = properties?.current_use || 'Unknown'
        const propertyId = properties?.id || 'N/A'

        popup.setLngLat(e.lngLat)
          .setHTML(`
            <div class="p-4 max-w-sm">
              <h3 class="font-bold text-lg text-gray-900 mb-2">${address}</h3>
              <div class="space-y-2 text-sm">
                <p><span class="font-medium">Use:</span> ${currentUse}</p>
                <p><span class="font-medium">ID:</span> ${propertyId}</p>
                <p class="text-xs text-gray-500 mt-2">Click to analyze this property</p>
              </div>
            </div>
          `)
          .addTo(mapInstance)
      }
    })

    // Add hover handlers for general properties
    mapInstance.on('mouseenter', 'general-properties', () => {
      mapInstance.getCanvas().style.cursor = 'pointer'
    })

    mapInstance.on('mouseleave', 'general-properties', () => {
      mapInstance.getCanvas().style.cursor = ''
    })

    return () => {
      popup.remove()
    }
  }, [])

  // Update map with property data
  useEffect(() => {
    if (!map.current || !mapLoaded) return

    const mapInstance = map.current

    // Clear existing property layers and sources first (only analysis-specific layers)
    const layersToClear = ['property-fill', 'property-outline', 'property-center', 'property-center-dot']
    if (analysis) {
      // When showing analysis, also clear general properties
      layersToClear.push('general-properties')
    }

    layersToClear.forEach(layerId => {
      if (mapInstance.getLayer(layerId)) {
        mapInstance.removeLayer(layerId)
      }
    })

    const sourcesToClear = ['property', 'zoning', 'landmarks']
    if (analysis) {
      // When showing analysis, also clear general properties source
      sourcesToClear.push('general-properties')
    }

    sourcesToClear.forEach(sourceId => {
      if (mapInstance.getSource(sourceId)) {
        mapInstance.removeSource(sourceId)
      }
    })

    // If we have specific analysis data, show that property
    if (analysis) {

    // Add property boundary
    if (analysis.property.latitude && analysis.property.longitude) {
      // Create a small polygon around the property point for visualization
      const propertyCoords = [
        [
          [analysis.property.longitude - 0.001, analysis.property.latitude - 0.001],
          [analysis.property.longitude + 0.001, analysis.property.latitude - 0.001],
          [analysis.property.longitude + 0.001, analysis.property.latitude + 0.001],
          [analysis.property.longitude - 0.001, analysis.property.latitude + 0.001],
          [analysis.property.longitude - 0.001, analysis.property.latitude - 0.001]
        ]
      ]

      // Remove existing property source if it exists
      if (mapInstance.getSource('property')) {
        mapInstance.removeSource('property')
      }

      mapInstance.addSource('property', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: propertyCoords
          },
          properties: {}
        }
      })

      if (layers.property) {
        // Property parcel fill
        mapInstance.addLayer({
          id: 'property-fill',
          type: 'fill',
          source: 'property',
          paint: {
            'fill-color': '#3b82f6',
            'fill-opacity': 0.4,
            'fill-outline-color': '#1d4ed8'
          }
        })

        // Property parcel outline
        mapInstance.addLayer({
          id: 'property-outline',
          type: 'line',
          source: 'property',
          paint: {
            'line-color': '#1d4ed8',
            'line-width': 3,
            'line-opacity': 0.9
          }
        })

        // Property center marker
        mapInstance.addLayer({
          id: 'property-center',
          type: 'circle',
          source: 'property',
          paint: {
            'circle-radius': 8,
            'circle-color': '#ffffff',
            'circle-stroke-width': 3,
            'circle-stroke-color': '#1d4ed8',
            'circle-opacity': 0.95,
            'circle-stroke-opacity': 1
          }
        })

        // Property center dot
        mapInstance.addLayer({
          id: 'property-center-dot',
          type: 'circle',
          source: 'property',
          paint: {
            'circle-radius': 4,
            'circle-color': '#1d4ed8',
            'circle-opacity': 1
          }
        })
      }

      // Center map on property
      mapInstance.flyTo({
        center: [analysis.property.longitude, analysis.property.latitude],
        zoom: 16,
        duration: 2000
      })
    }

    // Add zoning districts
    if (layers.zoning && analysis.zoning.zoning_districts.length > 0) {
      const zoningFeatures = analysis.zoning.zoning_districts.map((district: any) => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Polygon' as const,
          coordinates: [
            [
              [analysis.property.longitude! - 0.002, analysis.property.latitude! - 0.002],
              [analysis.property.longitude! + 0.002, analysis.property.latitude! - 0.002],
              [analysis.property.longitude! + 0.002, analysis.property.latitude! + 0.002],
              [analysis.property.longitude! - 0.002, analysis.property.latitude! + 0.002],
              [analysis.property.longitude! - 0.002, analysis.property.latitude! - 0.002]
            ]
          ]
        },
        properties: {
          code: district.district_code,
          name: district.district_name,
          far: district.far_base
        }
      }))

      // Remove existing zoning source if it exists
      if (mapInstance.getSource('zoning')) {
        mapInstance.removeSource('zoning')
      }

      mapInstance.addSource('zoning', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: zoningFeatures
        }
      })

      mapInstance.addLayer({
        id: 'zoning-fill',
        type: 'fill',
        source: 'zoning',
        paint: {
          'fill-color': [
            'match',
            ['get', 'code'],
            'R10', '#10b981',      // Residential - green
            'R8', '#059669',       // Residential - darker green
            'R6', '#047857',       // Residential - dark green
            'C6-4', '#f59e0b',     // Commercial - amber
            'C4', '#d97706',       // Commercial - orange
            'C2', '#92400e',       // Commercial - brown
            'M1-1', '#ef4444',     // Manufacturing - red
            'M2', '#dc2626',       // Manufacturing - darker red
            'M3', '#b91c1c',       // Manufacturing - dark red
            '#6b7280'              // default gray
          ],
          'fill-opacity': 0.25,
          // Add subtle glow effect
          'fill-outline-color': [
            'match',
            ['get', 'code'],
            'R10', '#34d399',
            'R8', '#10b981',
            'R6', '#059669',
            'C6-4', '#fbbf24',
            'C4', '#f59e0b',
            'C2', '#d97706',
            'M1-1', '#f87171',
            'M2', '#ef4444',
            'M3', '#dc2626',
            '#9ca3af'
          ]
        }
      })

      mapInstance.addLayer({
        id: 'zoning-outline',
        type: 'line',
        source: 'zoning',
        paint: {
          'line-color': [
            'match',
            ['get', 'code'],
            'R10', '#065f46',
            'R8', '#064e3b',
            'R6', '#022c22',
            'C6-4', '#92400e',
            'C4', '#78350f',
            'C2', '#451a03',
            'M1-1', '#7f1d1d',
            'M2', '#991b1b',
            'M3', '#7f1d1d',
            '#374151'
          ],
          'line-width': 2,
          'line-opacity': 0.8
        }
      })

      // Add zoning district labels
      mapInstance.addLayer({
        id: 'zoning-labels',
        type: 'symbol',
        source: 'zoning',
        layout: {
          'text-field': ['get', 'code'],
          'text-size': 12,
          'text-anchor': 'center',
          'text-justify': 'center',
          'text-allow-overlap': false,
          'text-ignore-placement': false
        },
        paint: {
          'text-color': '#1f2937',
          'text-halo-color': '#ffffff',
          'text-halo-width': 2,
          'text-opacity': 0.9
        },
        minzoom: 14
      })
    }

    // Add landmarks
    if (layers.landmarks && analysis.nearby_landmarks.length > 0) {
      const landmarkFeatures = analysis.nearby_landmarks.map(landmark => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [
            // Use actual coordinates if available, otherwise position around property
            landmark.longitude || (analysis.property.longitude! + (Math.random() - 0.5) * 0.003),
            landmark.latitude || (analysis.property.latitude! + (Math.random() - 0.5) * 0.003)
          ]
        },
        properties: {
          name: landmark.name,
          type: landmark.landmark_type,
          distance: landmark.distance_ft,
          description: landmark.description
        }
      }))

      // Remove existing landmarks source if it exists
      if (mapInstance.getSource('landmarks')) {
        mapInstance.removeSource('landmarks')
      }

      mapInstance.addSource('landmarks', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: landmarkFeatures
        }
      })

      // Add landmark circles with better styling
      mapInstance.addLayer({
        id: 'landmarks',
        type: 'circle',
        source: 'landmarks',
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            10, 6,
            16, 12
          ],
          'circle-color': [
            'match',
            ['get', 'type'],
            'historic', '#dc2626',
            'cultural', '#7c3aed',
            'natural', '#059669',
            'transportation', '#0891b2',
            '#6b7280' // default
          ],
          'circle-stroke-width': 3,
          'circle-stroke-color': '#ffffff',
          'circle-opacity': 0.9,
          'circle-stroke-opacity': 1
        }
      })

      // Add landmark labels
      mapInstance.addLayer({
        id: 'landmark-labels',
        type: 'symbol',
        source: 'landmarks',
        layout: {
          'text-field': ['get', 'name'],
          'text-size': [
            'interpolate',
            ['linear'],
            ['zoom'],
            12, 10,
            16, 14
          ],
          'text-anchor': 'bottom',
          'text-justify': 'center',
          'text-offset': [0, -1.5],
          'text-allow-overlap': false,
          'text-ignore-placement': false,
          'icon-image': [
            'match',
            ['get', 'type'],
            'historic', 'castle-15',
            'cultural', 'art-gallery-15',
            'natural', 'park-15',
            'transportation', 'rail-15',
            'religious', 'place-of-worship-15',
            'educational', 'school-15',
            'marker-15'
          ],
          'icon-size': 1.2,
          'icon-anchor': 'bottom',
          'icon-allow-overlap': false
        },
        paint: {
          'text-color': '#1f2937',
          'text-halo-color': '#ffffff',
          'text-halo-width': 2,
          'text-opacity': 0.9
        },
        minzoom: 13
      })
    }
    } // Close the analysis block

    // Show general property pins when property layer is enabled
    // (both in overview mode and analysis mode for context)
    if (generalProperties.length > 0 && layers.property) {
      // Filter out the currently analyzed property to avoid duplication
      const filteredProperties = generalProperties.filter(prop => {
        if (!prop.latitude || !prop.longitude) return false
        // Don't show the analyzed property as a general pin
        if (analysis?.property?.id === prop.id) return false
        return true
      })

      // Remove existing general-properties source if it exists
      if (mapInstance.getSource('general-properties')) {
        mapInstance.removeSource('general-properties')
      }

      const propertyFeatures = filteredProperties
        .map(prop => ({
          type: 'Feature' as const,
          geometry: {
            type: 'Point' as const,
            coordinates: [prop.longitude!, prop.latitude!]
          },
          properties: {
            id: prop.id,
            address: prop.address,
            current_use: prop.current_use
          }
        }))

      mapInstance.addSource('general-properties', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: propertyFeatures
        }
      })

      mapInstance.addLayer({
        id: 'general-properties',
        type: 'circle',
        source: 'general-properties',
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            10, 2,
            16, 6
          ],
          'circle-color': '#10b981',
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff',
          'circle-opacity': 0.8,
          'circle-stroke-opacity': 0.9
        },
        minzoom: 10
      })
    }
  }, [analysis, layers, generalProperties, mapLoaded])

  const toggleLayer = (layer: keyof typeof layers) => {
    setLayers(prev => ({ ...prev, [layer]: !prev[layer] }))
  }

  const zoomIn = () => {
    if (map.current) {
      map.current.zoomIn()
    }
  }

  const zoomOut = () => {
    if (map.current) {
      map.current.zoomOut()
    }
  }

  const locateProperty = () => {
    if (map.current && analysis?.property.latitude && analysis?.property.longitude) {
      map.current.flyTo({
        center: [analysis.property.longitude, analysis.property.latitude],
        zoom: 16,
        duration: 1000
      })
    }
  }

  return (
    <div className={`relative ${className}`}>
      <div
        ref={mapContainer}
        key="mapbox-container"
        className="w-full h-full min-h-[400px] rounded-lg overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        tabIndex={0}
        role="application"
        aria-label="Interactive zoning map of New York City"
        aria-describedby="map-instructions"
      />

      {/* Screen reader instructions */}
      <div id="map-instructions" className="sr-only">
        Interactive map showing zoning districts and landmarks. Use mouse to click on areas for details. Use layer controls to toggle different map layers.
      </div>

      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-75 rounded-lg">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading map...</span>
          </div>
        </div>
      )}

      {mapError && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-75 rounded-lg">
          <div className="flex items-center justify-center text-center p-4">
            <div>
              <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-2" />
              <p className="text-sm text-gray-700 mb-2">Map Error</p>
              <p className="text-xs text-gray-600 max-w-xs">{mapError}</p>
              <Button
                onClick={() => window.location.reload()}
                variant="outline"
                size="sm"
                className="mt-3"
              >
                Reload Page
              </Button>
            </div>
          </div>
        </div>
      )}

      {showControls && (
        <div className="absolute top-2 right-2 space-y-1.5">
          {/* Layer Controls - Compact Design */}
          <div className="neumorphism neumorphism-up neumorphism-rounded bg-white/90 backdrop-blur-sm p-2 space-y-2 min-w-[120px] border border-white/30 hover:bg-white/95 transition-all duration-200">
            <div className="flex items-center space-x-2 text-xs font-medium text-gray-700 px-1">
              <Layers className="h-3 w-3 text-blue-600" />
              <span>Layers</span>
            </div>

            {/* Layer Toggles - Compact */}
            <div className="space-y-1">
              <label className="flex items-center justify-between text-xs cursor-pointer py-1 px-2 hover:bg-blue-50 rounded transition-colors touch-manipulation focus-within:bg-blue-50">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 bg-blue-500 rounded-full opacity-80"></div>
                  <span>Property</span>
                </div>
                <input
                  type="checkbox"
                  checked={layers.property}
                  onChange={() => toggleLayer('property')}
                  className="rounded w-3 h-3 text-blue-600 focus:ring-blue-500 scale-75"
                  aria-label="Toggle property layer"
                />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer py-1 px-2 hover:bg-green-50 rounded transition-colors touch-manipulation focus-within:bg-green-50">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 bg-green-500 rounded opacity-80"></div>
                  <span>Zoning</span>
                </div>
                <input
                  type="checkbox"
                  checked={layers.zoning}
                  onChange={() => toggleLayer('zoning')}
                  className="rounded w-3 h-3 text-green-600 focus:ring-green-500 scale-75"
                  aria-label="Toggle zoning layer"
                />
              </label>

              <label className="flex items-center justify-between text-xs cursor-pointer py-1 px-2 hover:bg-purple-50 rounded transition-colors touch-manipulation focus-within:bg-purple-50">
                <div className="flex items-center space-x-2">
                  <div className="w-2.5 h-2.5 bg-purple-500 rounded-full opacity-80"></div>
                  <span>Landmarks</span>
                </div>
                <input
                  type="checkbox"
                  checked={layers.landmarks}
                  onChange={() => toggleLayer('landmarks')}
                  className="rounded w-3 h-3 text-purple-600 focus:ring-purple-500 scale-75"
                  aria-label="Toggle landmarks layer"
                />
              </label>
            </div>
          </div>

          {/* Zoom Controls - Compact */}
          <div className="neumorphism neumorphism-up neumorphism-rounded bg-white/90 backdrop-blur-sm p-2 border border-white/30 hover:bg-white/95 transition-all duration-200">
            <div className="flex flex-col space-y-1 items-center">
              {/* Zoom In */}
              <div className="flex flex-col items-center space-y-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={zoomIn}
                  className="p-1.5 hover:bg-gray-100 focus:bg-gray-100 touch-manipulation h-8 w-8 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                  aria-label="Zoom in on map"
                  title="Zoom In (+)"
                >
                  <ZoomIn className="h-3.5 w-3.5" />
                </Button>
                <span className="text-[10px] text-gray-600 font-medium leading-none">IN</span>
              </div>

              {/* Zoom Out */}
              <div className="flex flex-col items-center space-y-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={zoomOut}
                  className="p-1.5 hover:bg-gray-100 focus:bg-gray-100 touch-manipulation h-8 w-8 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                  aria-label="Zoom out on map"
                  title="Zoom Out (-)"
                >
                  <ZoomOut className="h-3.5 w-3.5" />
                </Button>
                <span className="text-[10px] text-gray-600 font-medium leading-none">OUT</span>
              </div>

              {/* Locate Property */}
              {analysis && (
                <div className="flex flex-col items-center space-y-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={locateProperty}
                    className="p-1.5 hover:bg-gray-100 focus:bg-gray-100 touch-manipulation h-8 w-8 focus:ring-1 focus:ring-blue-500 focus:outline-none"
                    aria-label="Center map on selected property"
                    title="Center on Property (fly to selected property location)"
                  >
                    <Locate className="h-3.5 w-3.5" />
                  </Button>
                  <span className="text-[10px] text-gray-600 font-medium leading-none">PROP</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}