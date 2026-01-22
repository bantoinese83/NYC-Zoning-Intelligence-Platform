export interface AirRights {
  property_id: string
  unused_far: number
  transferable_far: number
  adjacent_properties: number
  tdr_price_per_sf?: number
  estimated_value?: number
  potential_recipients?: AirRightsRecipient[]
}

export interface AirRightsRecipient {
  property_id: string
  address: string
  current_far: number
  max_far: number
  additional_potential_far: number
  additional_potential_sf: number
  distance_ft?: number
}

export interface AirRightsAnalysis {
  property_id: string
  unused_far: number
  transferable_far: number
  transferable_sf: number
  potential_recipients: AirRightsRecipient[]
  market_value: {
    price_per_sf: number
    total_value: number
    confidence: 'high' | 'medium' | 'low'
  }
  transfer_scenarios: TransferScenario[]
}

export interface TransferScenario {
  id: string
  recipient_property_id: string
  far_to_transfer: number
  recipient_benefit_sf: number
  market_value: number
  viability_score: number // 0-100
  constraints: string[]
}

export interface AirRightsMarketData {
  borough: string
  average_price_per_sf: number
  price_range: [number, number]
  recent_transactions_count: number
  trending: 'up' | 'down' | 'stable'
  last_updated: string
}

export interface AirRightsTransaction {
  id: string
  from_property_address: string
  to_property_address: string
  far_transferred: number
  price_per_sf: number
  total_value: number
  transaction_date: string
  verified: boolean
}