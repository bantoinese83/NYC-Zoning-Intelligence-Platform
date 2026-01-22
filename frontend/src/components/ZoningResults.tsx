'use client'

import { PropertyAnalysis } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Building, Ruler, DollarSign, MapPin, Home, CheckCircle, XCircle } from 'lucide-react'

interface ZoningResultsProps {
  analysis: PropertyAnalysis
  className?: string
}

export function ZoningResults({ analysis, className = "" }: ZoningResultsProps) {
  const { property, zoning, tax_incentives, air_rights, nearby_landmarks } = analysis

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Property Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Home className="h-5 w-5" />
            <span>{property.address}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Lot Number</span>
              <div className="font-medium">{property.lot_number}</div>
            </div>
            <div>
              <span className="text-gray-500">Block Number</span>
              <div className="font-medium">{property.block_number || 'N/A'}</div>
            </div>
            <div>
              <span className="text-gray-500">Land Area</span>
              <div className="font-medium">{property.land_area_sf?.toLocaleString()} SF</div>
            </div>
            <div>
              <span className="text-gray-500">Building Area</span>
              <div className="font-medium">{property.building_area_sf?.toLocaleString()} SF</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Zoning Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Building className="h-5 w-5" />
            <span>Zoning Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Overall FAR Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {zoning.total_far_base?.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Base FAR</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {zoning.total_far_with_bonuses?.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">FAR with Bonuses</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {zoning.total_buildable_area_sf?.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Buildable SF</div>
            </div>
          </div>

          {/* Zoning Districts */}
          <div>
            <h4 className="font-medium mb-3">Zoning Districts</h4>
            <div className="space-y-3">
              {zoning.zoning_districts?.map((district: any, index: number) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{district.district_code}</span>
                    <Badge variant="outline">
                      {district.percent_in_district}% of property
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">FAR Base</span>
                      <div>{district.far_base}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">FAR with Bonus</span>
                      <div>{district.far_with_bonus}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Max Height</span>
                      <div>{district.max_height_ft ? `${district.max_height_ft} ft` : 'N/A'}</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Setbacks</span>
                      <div>F: {district.setback_requirements.front_ft}ft</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Setback Requirements */}
          <div>
            <h4 className="font-medium mb-3 flex items-center space-x-2">
              <Ruler className="h-4 w-4" />
              <span>Setback Requirements</span>
            </h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-sm text-gray-500">Front</div>
                  <div className="font-medium">{zoning.setback_requirements?.front_ft || 0} ft</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Side</div>
                  <div className="font-medium">{zoning.setback_requirements?.side_ft || 0} ft</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Rear</div>
                  <div className="font-medium">{zoning.setback_requirements?.rear_ft || 0} ft</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tax Incentives */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>Tax Incentive Programs</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {tax_incentives.length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              No tax incentive programs analyzed
            </p>
          ) : (
            <div className="space-y-4">
              {tax_incentives.map((incentive, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium">{incentive.program_name}</span>
                    <div className="flex items-center space-x-2">
                      {incentive.is_eligible ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Eligible
                        </Badge>
                      ) : (
                        <Badge variant="destructive">
                          <XCircle className="h-3 w-3 mr-1" />
                          Not Eligible
                        </Badge>
                      )}
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">
                    {incentive.eligibility_reason}
                  </p>

                  {incentive.estimated_abatement_value && (
                    <div className="text-sm">
                      <span className="text-gray-500">Est. Annual Savings: </span>
                      <span className="font-medium text-green-600">
                        ${incentive.estimated_abatement_value.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Air Rights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Building className="h-5 w-5" />
            <span>Air Rights Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-xl font-bold text-orange-600">
                {air_rights.unused_far?.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Unused FAR</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-xl font-bold text-blue-600">
                {air_rights.transferable_far?.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Transferable FAR</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-xl font-bold text-purple-600">
                {air_rights.adjacent_properties}
              </div>
              <div className="text-sm text-gray-600">Adjacent Properties</div>
            </div>
          </div>

          {air_rights.estimated_value && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">
                  ${air_rights.estimated_value.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">
                  Estimated Market Value (at ${air_rights.tdr_price_per_sf}/SF)
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Nearby Landmarks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5" />
            <span>Nearby Landmarks</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {nearby_landmarks.length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              No landmarks found within 150 feet
            </p>
          ) : (
            <div className="space-y-3">
              {nearby_landmarks.slice(0, 10).map((landmark, index) => (
                <div key={index} className="flex items-center justify-between py-2 border-b last:border-b-0">
                  <div>
                    <div className="font-medium">{landmark.name}</div>
                    <div className="text-sm text-gray-500 capitalize">
                      {(landmark as any).landmark_type || landmark.type}
                    </div>
                  </div>
                  <Badge variant="outline">
                    {(landmark as any).distance_ft || landmark.distance} ft
                  </Badge>
                </div>
              ))}
              {nearby_landmarks.length > 10 && (
                <div className="text-center text-sm text-gray-500 pt-2">
                  +{nearby_landmarks.length - 10} more landmarks
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}