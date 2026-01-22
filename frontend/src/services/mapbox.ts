import mapboxgl from 'mapbox-gl'

// Initialize Mapbox with token
const initializeMapbox = () => {
  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN
  if (!token) {
    console.warn('Mapbox token not found. Maps will not function properly.')
    return false
  }

  mapboxgl.accessToken = token
  return true
}

// Geocoding service using Mapbox
export class MapboxGeocodingService {
  private static readonly BASE_URL = 'https://api.mapbox.com/geocoding/v5/mapbox.places'
  private static readonly TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

  static async geocodeAddress(address: string): Promise<{
    latitude: number
    longitude: number
    placeName: string
    bbox?: [number, number, number, number]
  } | null> {
    if (!this.TOKEN) {
      throw new Error('Mapbox token not configured')
    }

    try {
      const encodedAddress = encodeURIComponent(address)
      const url = `${this.BASE_URL}/${encodedAddress}.json?access_token=${this.TOKEN}&types=address&limit=1`

      const response = await fetch(url)
      const data = await response.json()

      if (!data.features || data.features.length === 0) {
        return null
      }

      const feature = data.features[0]
      const [longitude, latitude] = feature.center

      return {
        latitude,
        longitude,
        placeName: feature.place_name,
        bbox: feature.bbox
      }
    } catch (error) {
      console.error('Geocoding error:', error)
      throw new Error('Failed to geocode address')
    }
  }

  static async reverseGeocode(latitude: number, longitude: number): Promise<{
    address: string
    placeName: string
    context?: any[]
  } | null> {
    if (!this.TOKEN) {
      throw new Error('Mapbox token not configured')
    }

    try {
      const url = `${this.BASE_URL}/${longitude},${latitude}.json?access_token=${this.TOKEN}&types=address`

      const response = await fetch(url)
      const data = await response.json()

      if (!data.features || data.features.length === 0) {
        return null
      }

      const feature = data.features[0]

      return {
        address: feature.text,
        placeName: feature.place_name,
        context: feature.context
      }
    } catch (error) {
      console.error('Reverse geocoding error:', error)
      throw new Error('Failed to reverse geocode coordinates')
    }
  }

  static async searchPlaces(query: string, options: {
    proximity?: [number, number]
    bbox?: [number, number, number, number]
    types?: string[]
    limit?: number
  } = {}): Promise<Array<{
    id: string
    placeName: string
    latitude: number
    longitude: number
    type: string
    relevance: number
  }>> {
    if (!this.TOKEN) {
      throw new Error('Mapbox token not configured')
    }

    try {
      const params = new URLSearchParams({
        access_token: this.TOKEN,
        limit: (options.limit || 5).toString(),
      })

      if (options.proximity) {
        params.append('proximity', options.proximity.join(','))
      }

      if (options.bbox) {
        params.append('bbox', options.bbox.join(','))
      }

      if (options.types && options.types.length > 0) {
        params.append('types', options.types.join(','))
      }

      const encodedQuery = encodeURIComponent(query)
      const url = `${this.BASE_URL}/${encodedQuery}.json?${params}`

      const response = await fetch(url)
      const data = await response.json()

      if (!data.features) {
        return []
      }

      return data.features.map((feature: any) => ({
        id: feature.id,
        placeName: feature.place_name,
        latitude: feature.center[1],
        longitude: feature.center[0],
        type: feature.place_type[0],
        relevance: feature.relevance || 0
      }))
    } catch (error) {
      console.error('Places search error:', error)
      throw new Error('Failed to search places')
    }
  }
}

// Map styling utilities
export class MapboxStyleUtils {
  static readonly NYC_BOUNDS: [[number, number], [number, number]] = [
    [-74.25909, 40.477399], // Southwest
    [-73.700272, 40.917577]  // Northeast
  ]

  static getDefaultStyle(): string {
    return 'mapbox://styles/mapbox/light-v11'
  }

  static getSatelliteStyle(): string {
    return 'mapbox://styles/mapbox/satellite-v9'
  }

  static getStreetsStyle(): string {
    return 'mapbox://styles/mapbox/streets-v12'
  }

  static createPropertyMarker(coordinates: [number, number]): mapboxgl.Marker {
    const el = document.createElement('div')
    el.className = 'property-marker'
    el.style.width = '24px'
    el.style.height = '24px'
    el.style.borderRadius = '50%'
    el.style.backgroundColor = '#3b82f6'
    el.style.border = '3px solid white'
    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)'

    return new mapboxgl.Marker(el)
      .setLngLat(coordinates)
  }

  static createLandmarkMarker(
    coordinates: [number, number],
    type: 'historic' | 'cultural' | 'natural' | 'transportation' | 'religious' | 'educational'
  ): mapboxgl.Marker {
    const colors = {
      historic: '#dc2626',
      cultural: '#7c3aed',
      natural: '#059669',
      transportation: '#0891b2',
      religious: '#d97706',
      educational: '#7c2d12'
    }

    const el = document.createElement('div')
    el.className = 'landmark-marker'
    el.style.width = '16px'
    el.style.height = '16px'
    el.style.borderRadius = '50%'
    el.style.backgroundColor = colors[type] || '#6b7280'
    el.style.border = '2px solid white'
    el.style.boxShadow = '0 1px 3px rgba(0,0,0,0.3)'

    return new mapboxgl.Marker(el)
      .setLngLat(coordinates)
  }
}

// Directions service
export class MapboxDirectionsService {
  private static readonly BASE_URL = 'https://api.mapbox.com/directions/v5/mapbox'
  private static readonly TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

  static async getWalkingDirections(
    from: [number, number],
    to: [number, number]
  ): Promise<{
    distance: number // in meters
    duration: number // in seconds
    geometry: any // GeoJSON LineString
  } | null> {
    if (!this.TOKEN) {
      throw new Error('Mapbox token not configured')
    }

    try {
      const coordinates = `${from[0]},${from[1]};${to[0]},${to[1]}`
      const url = `${this.BASE_URL}/walking/${coordinates}?access_token=${this.TOKEN}&geometries=geojson`

      const response = await fetch(url)
      const data = await response.json()

      if (!data.routes || data.routes.length === 0) {
        return null
      }

      const route = data.routes[0]

      return {
        distance: route.distance,
        duration: route.duration,
        geometry: route.geometry
      }
    } catch (error) {
      console.error('Directions error:', error)
      throw new Error('Failed to get directions')
    }
  }
}

// Initialize on module load
initializeMapbox()

const mapboxService = {
  initializeMapbox,
  MapboxGeocodingService,
  MapboxStyleUtils,
  MapboxDirectionsService
}

export default mapboxService