/**
 * Centralized error handling utilities for consistent error management.
 */

import { ERROR_MESSAGES } from './constants'

export interface AppError {
  message: string
  code: string
  details?: Record<string, unknown>
  timestamp: Date
  context?: string
}

export class ApplicationError extends Error {
  public readonly code: string
  public readonly details?: Record<string, unknown>
  public readonly timestamp: Date
  public readonly context?: string

  constructor(
    message: string,
    code: string,
    details?: Record<string, unknown>,
    context?: string
  ) {
    super(message)
    this.name = 'ApplicationError'
    this.code = code
    this.details = details
    this.timestamp = new Date()
    this.context = context
  }
}

/**
 * Creates a standardized error object from various error sources.
 */
export function normalizeError(error: unknown, context?: string): AppError {
  // Handle ApplicationError instances
  if (error instanceof ApplicationError) {
    return {
      message: error.message,
      code: error.code,
      details: error.details,
      timestamp: error.timestamp,
      context: error.context,
    }
  }

  // Handle standard Error instances
  if (error instanceof Error) {
    return {
      message: error.message,
      code: 'UNKNOWN_ERROR',
      timestamp: new Date(),
      context,
    }
  }

  // Handle API error responses
  if (typeof error === 'object' && error !== null) {
    const apiError = error as any
    if (apiError.message || apiError.error) {
      return {
        message: apiError.message || apiError.error,
        code: apiError.code || 'API_ERROR',
        details: apiError.details,
        timestamp: new Date(),
        context,
      }
    }
  }

  // Handle string errors
  if (typeof error === 'string') {
    return {
      message: error,
      code: 'UNKNOWN_ERROR',
      timestamp: new Date(),
      context,
    }
  }

  // Fallback for unknown error types
  return {
    message: ERROR_MESSAGES.SERVER_ERROR,
    code: 'UNKNOWN_ERROR',
    timestamp: new Date(),
    context,
  }
}

/**
 * Gets user-friendly error message based on error code.
 */
export function getErrorMessage(error: AppError): string {
  // Use predefined messages for known error codes
  const predefinedMessage = ERROR_MESSAGES[error.code as keyof typeof ERROR_MESSAGES]
  if (predefinedMessage) {
    return predefinedMessage
  }

  // Return the original message if it's user-friendly, otherwise use a generic message
  if (error.message && error.message.length < 100 && !error.message.includes('Error:')) {
    return error.message
  }

  return ERROR_MESSAGES.SERVER_ERROR
}

/**
 * Logs error with appropriate level and context.
 */
export function logError(error: AppError, additionalContext?: Record<string, unknown>): void {
  const logData = {
    ...error,
    additionalContext,
  }

  // In development, log everything
  if (process.env.NODE_ENV === 'development') {
    console.error('Application Error:', logData)
    return
  }

  // In production, log based on error severity
  const isSevere = ['NETWORK_ERROR', 'SERVER_ERROR', 'UNKNOWN_ERROR'].includes(error.code)

  if (isSevere) {
    console.error('Severe Application Error:', logData)
  } else {
    console.warn('Application Warning:', logData)
  }

  // TODO: Send to error reporting service (e.g., Sentry) in production
  // errorReportingService.captureException(error, { extra: logData })
}

/**
 * Handles async errors in React components.
 */
export function handleAsyncError<T extends any[]>(
  fn: (...args: T) => Promise<unknown>,
  context?: string
) {
  return async (...args: T): Promise<void> => {
    try {
      await fn(...args)
    } catch (error) {
      const normalizedError = normalizeError(error, context)
      logError(normalizedError)
      throw normalizedError
    }
  }
}

/**
 * Creates a standardized error boundary error handler.
 */
export function createErrorBoundaryHandler(componentName: string) {
  return (error: Error, errorInfo: { componentStack: string }) => {
    const appError: AppError = {
      message: error.message,
      code: 'REACT_ERROR',
      details: {
        componentName,
        componentStack: errorInfo.componentStack,
        stack: error.stack,
      },
      timestamp: new Date(),
      context: `React Error Boundary: ${componentName}`,
    }

    logError(appError)

    // TODO: Send to error reporting service
    // errorReportingService.captureException(appError)
  }
}

/**
 * Retry utility for failed operations.
 */
export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000,
  context?: string
): Promise<T> {
  let lastError: unknown

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation()
    } catch (error) {
      lastError = error

      if (attempt === maxRetries) {
        break
      }

      // Exponential backoff
      const waitTime = delay * Math.pow(2, attempt - 1)
      await new Promise(resolve => setTimeout(resolve, waitTime))

      logError(normalizeError(error, context), {
        attempt,
        maxRetries,
        nextRetryIn: waitTime,
      })
    }
  }

  throw normalizeError(lastError, context)
}

/**
 * Type guard to check if an error is an ApplicationError.
 */
export function isApplicationError(error: unknown): error is ApplicationError {
  return error instanceof ApplicationError
}

/**
 * Type guard to check if an error is retryable.
 */
export function isRetryableError(error: AppError): boolean {
  const retryableCodes = ['NETWORK_ERROR', 'TIMEOUT_ERROR']
  return retryableCodes.includes(error.code)
}