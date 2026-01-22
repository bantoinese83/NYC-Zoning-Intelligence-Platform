'use client'

import { useState } from 'react'
import { FileText, Download, Loader2, CheckCircle } from 'lucide-react'
import { useGeneratePDF } from '@/hooks/useGeneratePDF'
import { PropertyAnalysis } from '@/types'
import { Button } from './ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Checkbox } from './ui/Checkbox'

interface ReportGeneratorProps {
  propertyId: string
  analysis?: PropertyAnalysis
  className?: string
}

interface ReportOptions {
  include_zoning: boolean
  include_incentives: boolean
  include_landmarks: boolean
  include_air_rights: boolean
  include_valuation: boolean
}

export function ReportGenerator({
  propertyId,
  analysis,
  className = ""
}: ReportGeneratorProps) {
  const [options, setOptions] = useState<ReportOptions>({
    include_zoning: true,
    include_incentives: true,
    include_landmarks: true,
    include_air_rights: true,
    include_valuation: true
  })

  const { mutate: generatePDF, isPending, isSuccess, error } = useGeneratePDF()

  const handleGenerate = () => {
    generatePDF({
      property_id: propertyId,
      ...options
    })
  }

  const updateOption = (key: keyof ReportOptions) => {
    setOptions(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const selectedSections = Object.values(options).filter(Boolean).length

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="h-5 w-5" />
          <span>Generate Zoning Report</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Report Preview */}
        {analysis && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Report Preview</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <div>Property: {analysis.property.address}</div>
              <div>Zoning Districts: {analysis.zoning.zoning_districts?.length || 0}</div>
              <div>Tax Incentives: {analysis.tax_incentives.length} programs</div>
              <div>Nearby Landmarks: {analysis.nearby_landmarks.length}</div>
              <div>Air Rights: {analysis.air_rights.unused_far?.toFixed(2)} unused FAR</div>
            </div>
          </div>
        )}

        {/* Report Options */}
        <div className="space-y-3">
          <h4 className="font-medium">Include in Report:</h4>

          <div className="space-y-3">
            <Checkbox
              id="zoning"
              checked={options.include_zoning}
              onChange={() => updateOption('include_zoning')}
              label="Zoning Analysis & FAR Calculations"
              description="District codes, buildable area, height restrictions"
            />

            <Checkbox
              id="incentives"
              checked={options.include_incentives}
              onChange={() => updateOption('include_incentives')}
              label="Tax Incentive Programs"
              description="Eligibility for 467-M, ICAP, and other programs"
            />

            <Checkbox
              id="landmarks"
              checked={options.include_landmarks}
              onChange={() => updateOption('include_landmarks')}
              label="Nearby Landmarks"
              description="Historic, cultural, and natural landmarks within 150 feet"
            />

            <Checkbox
              id="air-rights"
              checked={options.include_air_rights}
              onChange={() => updateOption('include_air_rights')}
              label="Air Rights Analysis"
              description="Unused FAR and transfer opportunities"
            />

            <Checkbox
              id="valuation"
              checked={options.include_valuation}
              onChange={() => updateOption('include_valuation')}
              label="Property Valuation"
              description="Estimated development value and market analysis"
            />
          </div>
        </div>

        {/* Generate Button */}
        <div className="pt-4 border-t">
          <Button
            onClick={handleGenerate}
            disabled={isPending || selectedSections === 0}
            className="w-full"
            size="lg"
          >
            {isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating Report...
              </>
            ) : isSuccess ? (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Report Generated!
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Generate PDF Report ({selectedSections} sections)
              </>
            )}
          </Button>

          {selectedSections === 0 && (
            <p className="text-sm text-red-600 mt-2 text-center">
              Please select at least one section to include in the report
            </p>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              Failed to generate report: {error.message}
            </p>
          </div>
        )}

        {/* Report Information */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>• Reports are generated in PDF format</p>
          <p>• Processing typically takes 10-30 seconds</p>
          <p>• File size is approximately 2-5 MB</p>
          <p>• Reports include all charts, maps, and detailed analysis</p>
        </div>
      </CardContent>
    </Card>
  )
}