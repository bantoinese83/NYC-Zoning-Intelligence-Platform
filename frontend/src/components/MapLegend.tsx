'use client'

export function MapLegend() {
  return (
    <div className="w-full max-w-6xl mx-auto mt-6">
      <div className="neumorphism neumorphism-card neumorphism-rounded bg-white/95 backdrop-blur-sm border border-white/20 p-6">
        <div className="text-center mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-2">Map Legend</h3>
          <p className="text-sm text-gray-600">Understanding the zoning districts and landmarks on the map</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Zoning Districts */}
          <div>
            <h4 className="text-sm font-semibold text-gray-800 mb-4 flex items-center">
              <div className="w-4 h-4 bg-gradient-to-br from-green-500 to-green-600 rounded mr-2"></div>
              Zoning Districts
            </h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded opacity-80"></div>
                  <span className="text-gray-600">R10 (High-Density)</span>
                </div>
                <span className="text-xs text-gray-500">Residential</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-600 rounded opacity-80"></div>
                  <span className="text-gray-600">R8/R6 (Mid-Density)</span>
                </div>
                <span className="text-xs text-gray-500">Residential</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-amber-500 rounded opacity-80"></div>
                  <span className="text-gray-600">C6-4 (Commercial)</span>
                </div>
                <span className="text-xs text-gray-500">Commercial</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-amber-600 rounded opacity-80"></div>
                  <span className="text-gray-600">C4/C2 (Local Comm.)</span>
                </div>
                <span className="text-xs text-gray-500">Commercial</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded opacity-80"></div>
                  <span className="text-gray-600">M1-1 (Light Mfg)</span>
                </div>
                <span className="text-xs text-gray-500">Manufacturing</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-600 rounded opacity-80"></div>
                  <span className="text-gray-600">M2/M3 (Heavy Mfg)</span>
                </div>
                <span className="text-xs text-gray-500">Manufacturing</span>
              </div>
            </div>
          </div>

          {/* Landmarks */}
          <div>
            <h4 className="text-sm font-semibold text-gray-800 mb-4 flex items-center">
              <div className="w-4 h-4 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full mr-2"></div>
              Landmarks & Points of Interest
            </h4>
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-gray-600">Historic Landmarks</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-gray-600">Cultural Venues</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                <span className="text-gray-600">Natural Features</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-gray-600">Transportation Hubs</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-indigo-500 rounded-full"></div>
                <span className="text-gray-600">Religious Sites</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="text-gray-600">Educational Facilities</span>
              </div>
            </div>
          </div>

          {/* Property & Controls */}
          <div>
            <h4 className="text-sm font-semibold text-gray-800 mb-4 flex items-center">
              <div className="w-4 h-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full mr-2"></div>
              Property & Controls
            </h4>
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-blue-500 rounded-full border border-white"></div>
                <span className="text-gray-600">Selected Property</span>
              </div>
              <div className="text-xs text-gray-500 mt-4">
                <p className="mb-2"><strong>Interactive Features:</strong></p>
                <ul className="space-y-1 text-xs">
                  <li>• Click zoning areas for details</li>
                  <li>• Click landmarks for information</li>
                  <li>• Use layer controls to toggle visibility</li>
                  <li>• Zoom and pan to explore</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap justify-center gap-4 text-xs text-gray-500">
            <span className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded mr-1"></div>
              Click for zoning details
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-1"></div>
              Click for landmark info
            </span>
            <span>Scroll to zoom • Drag to pan</span>
          </div>
        </div>
      </div>
    </div>
  )
}