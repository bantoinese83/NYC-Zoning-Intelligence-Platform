'use client'

import { useState } from 'react'
import type { AppProps } from 'next/app'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import '@/styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes - data stays fresh longer
        gcTime: 30 * 60 * 1000, // 30 minutes - keep in cache longer
        retry: (failureCount, error) => {
          // Don't retry on 4xx errors
          if (error instanceof Error && 'status' in error && typeof error.status === 'number') {
            if (error.status >= 400 && error.status < 500) {
              return false
            }
          }
          return failureCount < 3
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        // Enable background refetching for better UX
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        // Network mode optimizations
        networkMode: 'online',
      },
      mutations: {
        retry: false, // Don't retry mutations by default
        // Add optimistic updates for better UX
        onError: (error, _variables, _context) => {
          // Error handling can be enhanced here
          console.error('Mutation error:', error)
        },
      },
    },
  }))

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Component {...pageProps} />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}