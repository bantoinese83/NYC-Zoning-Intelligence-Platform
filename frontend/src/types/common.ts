// Common types used across the application

export interface Coordinates {
  latitude: number
  longitude: number
}

export interface Bounds {
  north: number
  south: number
  east: number
  west: number
}

export interface Address {
  street: string
  city: string
  state: string
  zip_code: string
  full_address: string
}

export interface ContactInfo {
  email?: string
  phone?: string
  website?: string
}

export interface Timestamped {
  created_at: string
  updated_at: string
}

export interface Identifiable {
  id: string
}

export interface Named {
  name: string
}

// Form types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'number' | 'select' | 'textarea' | 'checkbox'
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  validation?: {
    min?: number
    max?: number
    pattern?: string
    custom?: (value: any) => string | null
  }
}

export interface FormState {
  isSubmitting: boolean
  isValid: boolean
  errors: Record<string, string>
  touched: Record<string, boolean>
}

// Component props
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
  testId?: string
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'sm' | 'md' | 'lg'
  message?: string
}

export interface ErrorProps extends BaseComponentProps {
  error: Error | string
  onRetry?: () => void
  showDetails?: boolean
}

// Map component types
export interface MapMarker {
  id: string
  coordinates: Coordinates
  type: 'property' | 'landmark' | 'district'
  popup?: {
    title: string
    description?: string
    actions?: Array<{
      label: string
      onClick: () => void
    }>
  }
}

export interface MapLayer {
  id: string
  type: 'fill' | 'line' | 'circle' | 'symbol'
  source: any
  visible: boolean
  opacity?: number
  color?: string
}

// UI State types
export type Theme = 'light' | 'dark' | 'auto'

export interface NotificationItem {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}

// Search and filter types
export interface SearchFilters {
  query?: string
  type?: string
  bounds?: Bounds
  limit?: number
  offset?: number
}

export interface SortOption {
  field: string
  direction: 'asc' | 'desc'
  label: string
}

// Data table types
export interface TableColumn<T = any> {
  key: keyof T
  header: string
  sortable?: boolean
  render?: (value: any, row: T) => React.ReactNode
  width?: string | number
}

export interface TableProps<T = any> {
  data: T[]
  columns: TableColumn<T>[]
  loading?: boolean
  emptyMessage?: string
  onSort?: (column: keyof T, direction: 'asc' | 'desc') => void
  onRowClick?: (row: T) => void
  pagination?: {
    page: number
    limit: number
    total: number
    onPageChange: (page: number) => void
  }
}

// Modal and overlay types
export interface ModalProps extends BaseComponentProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  closable?: boolean
}

export interface DrawerProps extends BaseComponentProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  position?: 'left' | 'right' | 'top' | 'bottom'
  size?: string | number
}

// Export/import types
export interface ExportOptions {
  format: 'csv' | 'json' | 'pdf'
  filename?: string
  includeHeaders?: boolean
  columns?: string[]
}

export interface ImportResult {
  success: number
  errors: Array<{
    row: number
    field?: string
    message: string
  }>
  total: number
}