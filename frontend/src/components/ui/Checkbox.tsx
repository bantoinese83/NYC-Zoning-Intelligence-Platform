'use client'

import React from 'react'
import { cn } from '@/utils/cn'

export interface CheckboxProps {
  id: string
  checked: boolean
  onChange: (checked: boolean) => void
  label: string
  description?: string
  disabled?: boolean
  className?: string
}

export function Checkbox({
  id,
  checked,
  onChange,
  label,
  description,
  disabled = false,
  className = ""
}: CheckboxProps) {
  return (
    <div className={cn("flex items-start space-x-3", className)}>
      <div className="flex items-center h-5">
        <input
          id={id}
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className={cn(
            "h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded",
            "focus:ring-2 focus:ring-offset-2",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        />
      </div>
      <div className="flex-1 min-w-0">
        <label
          htmlFor={id}
          className={cn(
            "text-sm font-medium text-gray-900 cursor-pointer",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          {label}
        </label>
        {description && (
          <p className={cn(
            "text-sm text-gray-500 mt-1",
            disabled && "opacity-50"
          )}>
            {description}
          </p>
        )}
      </div>
    </div>
  )
}