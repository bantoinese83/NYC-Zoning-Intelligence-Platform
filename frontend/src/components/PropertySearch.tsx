'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Search, MapPin, Loader2, AlertTriangle } from 'lucide-react'
import { useSearchProperties } from '@/hooks/useSearchProperties'
import { Property } from '@/types'
import { Input } from './ui/Input'

interface PropertySearchProps {
  onPropertySelect: (property: Property) => void
  placeholder?: string
  className?: string
  initialQuery?: string
}

export function PropertySearch({
  onPropertySelect,
  placeholder = "Enter NYC property address...",
  className = "",
  initialQuery = ""
}: PropertySearchProps) {
  const [query, setQuery] = useState('')
  const hasSetInitialQuery = useRef(false)
  const [isOpen, setIsOpen] = useState(false)
  const [searchParams, setSearchParams] = useState<{address: string, city: string, state: string} | null>(null)

  // Set initial query when it changes
  React.useEffect(() => {
    if (initialQuery && !hasSetInitialQuery.current) {
      setQuery(initialQuery)
      hasSetInitialQuery.current = true
    }
  }, [initialQuery])

  const { data: results = [], isLoading: loading, error } = useSearchProperties(searchParams)

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.length >= 3) {
        setSearchParams({
          address: query,
          city: 'New York',
          state: 'NY'
        })
        setIsOpen(true)
      } else {
        setIsOpen(false)
        setSearchParams(null)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query])



  const handleSelect = useCallback((property: Property) => {
    if (!property || !property.id || !property.address) {
      console.warn('Invalid property selected:', property)
      return
    }

    setQuery(property.address)
    setIsOpen(false)
    onPropertySelect(property)
  }, [onPropertySelect])

  const handleInputChange = (value: string) => {
    setQuery(value)
    if (value.length < 3) {
      setIsOpen(false)
    }
  }

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <Input
          type="text"
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={placeholder}
          className="pr-12 min-h-[48px] text-base"
          maxLength={200}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="words"
          spellCheck="false"
          inputMode="text"
          onFocus={() => query.length >= 3 && setIsOpen(true)}
        />
        <div className="absolute inset-y-0 right-0 flex items-center pr-3">
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
          ) : (
            <Search className="h-4 w-4 text-gray-400" />
          )}
        </div>
      </div>

      {/* Search Results Dropdown */}
      {isOpen && (results.length > 0 || loading || error) && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-64 overflow-y-auto">
          {loading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              <span className="text-sm text-gray-500">Searching...</span>
            </div>
          )}

          {error && (
            <div className="px-4 py-3 text-sm text-red-600 bg-red-50 border-b">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-medium">{error.message || 'Search failed'}</div>
                  {'code' in error && error.code === 'NETWORK_ERROR' && (
                    <div className="text-xs text-red-500 mt-1">
                      Check your internet connection and try again.
                    </div>
                  )}
                  {'code' in error && error.code === 'VALIDATION_ERROR' && 'details' in error && error.details ? (
                    <div className="text-xs text-red-500 mt-1">
                      {Object.entries(error.details as Record<string, unknown>).map(([field, message]: [string, unknown]) => (
                        <div key={field}>{field}: {String(message)}</div>
                      ))}
                    </div>
                  ) : null}
                  {process.env.NODE_ENV === 'development' && 'details' in error && error.details ? (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-xs opacity-75">Technical Details</summary>
                      <pre className="text-xs mt-1 whitespace-pre-wrap">
                        {JSON.stringify(error.details as Record<string, unknown>, null, 2)}
                      </pre>
                    </details>
                  ) : null}
                </div>
              </div>
            </div>
          )}

          {!loading && !error && results.length === 0 && query.length >= 3 && (
            <div className="px-4 py-3 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4" />
                <span>No properties found for &ldquo;{query}&rdquo;</span>
              </div>
              <div className="text-xs mt-1 ml-6">
                Try a different address or check the spelling. Only NYC properties are supported.
              </div>
            </div>
          )}

          {!loading && !error && results.length === 0 && query.length === 0 && (
            <div className="px-4 py-3 text-sm text-gray-400">
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4" />
                <span>Start typing an address to search...</span>
              </div>
            </div>
          )}

          {results.length > 0 && (
            <div className="py-1">
              {results.slice(0, 10).map((property) => (
                <button
                  key={property.id}
                  onClick={() => handleSelect(property)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors touch-manipulation min-h-[44px]"
                >
                  <div className="flex items-start space-x-3">
                    <MapPin className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {property.address}
                      </div>
                      <div className="text-xs text-gray-500">
                        Lot {property.lot_number}
                        {property.block_number && ` • Block ${property.block_number}`}
                        {property.zip_code && ` • ${property.zip_code}`}
                      </div>
                      {property.building_area_sf && (
                        <div className="text-xs text-gray-500">
                          {property.building_area_sf.toLocaleString()} SF building
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}

              {results.length > 10 && (
                <div className="px-4 py-2 text-xs text-gray-500 border-t bg-gray-50">
                  +{results.length - 10} more results
                </div>
              )}
            </div>
          )}

          {!loading && !error && results.length === 0 && query.length >= 3 && (
            <div className="px-4 py-3 text-sm text-gray-500">
              No properties found for &quot;{query}&quot;
            </div>
          )}
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}