'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import { MapViewport } from '@/types'

// NYC default viewport
const NYC_VIEWPORT: MapViewport = {
  latitude: 40.7128,
  longitude: -74.0060,
  zoom: 12,
  bearing: 0,
  pitch: 0
}

interface UseMapOptions {
  initialViewport?: Partial<MapViewport>
  onViewportChange?: (viewport: MapViewport) => void
  interactive?: boolean
  showControls?: boolean
}

export function useMap(options: UseMapOptions = {}) {
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)

  const [isLoaded, setIsLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [viewport, setViewport] = useState<MapViewport>({
    ...NYC_VIEWPORT,
    ...options.initialViewport
  })

  // Initialize map
  const initializeMap = useCallback((container: HTMLDivElement) => {
    if (mapRef.current || !container) return

    const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN
    if (!mapboxToken) {
      setError('Mapbox token not configured')
      return
    }

    try {
      mapboxgl.accessToken = mapboxToken

      mapRef.current = new mapboxgl.Map({
        container,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [viewport.longitude, viewport.latitude],
        zoom: viewport.zoom,
        bearing: viewport.bearing || 0,
        pitch: viewport.pitch || 0,
        interactive: options.interactive !== false,
        attributionControl: false,
      })

      // Add navigation controls if requested
      if (options.showControls) {
        mapRef.current.addControl(new mapboxgl.NavigationControl(), 'top-right')
        mapRef.current.addControl(new mapboxgl.ScaleControl(), 'bottom-left')
      }

      mapRef.current.on('load', () => {
        setIsLoaded(true)
        setError(null)
      })

      mapRef.current.on('error', (e) => {
        setError(e.error?.message || 'Map failed to load')
        console.error('Mapbox error:', e)
      })

      // Handle viewport changes
      const handleMove = () => {
        if (!mapRef.current) return

        const center = mapRef.current.getCenter()
        const newViewport: MapViewport = {
          latitude: center.lat,
          longitude: center.lng,
          zoom: mapRef.current.getZoom(),
          bearing: mapRef.current.getBearing(),
          pitch: mapRef.current.getPitch()
        }

        setViewport(newViewport)
        options.onViewportChange?.(newViewport)
      }

      mapRef.current.on('moveend', handleMove)
      mapRef.current.on('zoomend', handleMove)
      mapRef.current.on('rotateend', handleMove)
      mapRef.current.on('pitchend', handleMove)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize map')
      console.error('Map initialization error:', err)
    }
  }, [viewport, options])

  // Cleanup map on unmount
  useEffect(() => {
    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
        setIsLoaded(false)
      }
    }
  }, [])

  // Map control methods
  const flyTo = useCallback((targetViewport: Partial<MapViewport>, options?: mapboxgl.FlyToOptions) => {
    if (!mapRef.current) return

    mapRef.current.flyTo({
      center: [targetViewport.longitude ?? viewport.longitude, targetViewport.latitude ?? viewport.latitude],
      zoom: targetViewport.zoom ?? viewport.zoom,
      bearing: targetViewport.bearing ?? viewport.bearing,
      pitch: targetViewport.pitch ?? viewport.pitch,
      ...options
    })
  }, [viewport])

  const zoomIn = useCallback(() => {
    if (!mapRef.current) return
    mapRef.current.zoomIn()
  }, [])

  const zoomOut = useCallback(() => {
    if (!mapRef.current) return
    mapRef.current.zoomOut()
  }, [])

  const resetView = useCallback(() => {
    flyTo(NYC_VIEWPORT)
  }, [flyTo])

  const fitBounds = useCallback((bounds: [[number, number], [number, number]], options?: mapboxgl.FitBoundsOptions) => {
    if (!mapRef.current) return

    mapRef.current.fitBounds(bounds, {
      padding: 20,
      ...options
    })
  }, [])

  // Layer management
  const addSource = useCallback((id: string, source: mapboxgl.AnySourceData) => {
    if (!mapRef.current || !isLoaded) return

    if (mapRef.current.getSource(id)) {
      mapRef.current.removeSource(id)
    }

    mapRef.current.addSource(id, source)
  }, [isLoaded])

  const addLayer = useCallback((layer: mapboxgl.AnyLayer, beforeId?: string) => {
    if (!mapRef.current || !isLoaded) return

    if (mapRef.current.getLayer(layer.id)) {
      mapRef.current.removeLayer(layer.id)
    }

    mapRef.current.addLayer(layer, beforeId)
  }, [isLoaded])

  const removeLayer = useCallback((id: string) => {
    if (!mapRef.current || !isLoaded) return

    if (mapRef.current.getLayer(id)) {
      mapRef.current.removeLayer(id)
    }
  }, [isLoaded])

  const setLayoutProperty = useCallback((layerId: string, name: string, value: any) => {
    if (!mapRef.current || !isLoaded) return
    mapRef.current.setLayoutProperty(layerId, name, value)
  }, [isLoaded])

  const setPaintProperty = useCallback((layerId: string, name: string, value: any) => {
    if (!mapRef.current || !isLoaded) return
    mapRef.current.setPaintProperty(layerId, name, value)
  }, [isLoaded])

  return {
    // Refs
    containerRef,
    mapRef: mapRef.current,

    // State
    isLoaded,
    error,
    viewport,

    // Initialization
    initializeMap,

    // Controls
    flyTo,
    zoomIn,
    zoomOut,
    resetView,
    fitBounds,

    // Layers
    addSource,
    addLayer,
    removeLayer,
    setLayoutProperty,
    setPaintProperty,
  }
}

// Hook for property-specific map interactions
export function usePropertyMap(propertyId?: string) {
  const map = useMap({
    interactive: true,
    showControls: true,
  })

  // Focus on property when ID changes
  useEffect(() => {
    if (!propertyId || !map.isLoaded) return

    // In a real implementation, you'd fetch property coordinates
    // For now, just center on NYC
    map.flyTo({
      latitude: 40.7128,
      longitude: -74.0060,
      zoom: 16
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [propertyId, map.isLoaded])

  return map
}