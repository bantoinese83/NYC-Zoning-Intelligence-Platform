/**
 * Performance optimization utilities for React components and hooks.
 */

import React, { useCallback, useMemo, useRef, useEffect } from 'react'

/**
 * Memoizes a value with deep comparison of dependencies.
 */
export function useDeepMemo<T>(factory: () => T, deps: React.DependencyList): T {
  const ref = useRef<{ deps: React.DependencyList; value: T }>()

  if (!ref.current || !depsEqual(ref.current.deps, deps)) {
    ref.current = { deps, value: factory() }
  }

  return ref.current.value
}

/**
 * Checks if two dependency arrays are equal.
 */
function depsEqual(a: React.DependencyList, b: React.DependencyList): boolean {
  if (a.length !== b.length) return false

  for (let i = 0; i < a.length; i++) {
    if (!Object.is(a[i], b[i])) return false
  }

  return true
}

/**
 * Debounced callback hook with automatic cleanup.
 */
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const callbackRef = useRef(callback)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  callbackRef.current = callback

  const debouncedCallback = useCallback(
    ((...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args)
      }, delay)
    }) as T,
    [delay]
  )

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return debouncedCallback
}

/**
 * Throttled callback hook with automatic cleanup.
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const callbackRef = useRef(callback)
  const lastCallRef = useRef<number>(0)

  callbackRef.current = callback

  const throttledCallback = useCallback(
    ((...args: Parameters<T>) => {
      const now = Date.now()

      if (now - lastCallRef.current >= delay) {
        lastCallRef.current = now
        callbackRef.current(...args)
      }
    }) as T,
    [delay]
  )

  return throttledCallback
}

/**
 * Memoizes an expensive computation with TTL (time-to-live).
 */
export function useMemoWithTTL<T>(
  factory: () => T,
  deps: React.DependencyList,
  ttlMs: number
): T {
  const ref = useRef<{ value: T; timestamp: number; deps: React.DependencyList }>()

  const now = Date.now()
  const isExpired = ref.current && (now - ref.current.timestamp) > ttlMs
  const depsChanged = !ref.current || !depsEqual(ref.current.deps, deps)

  if (!ref.current || isExpired || depsChanged) {
    ref.current = {
      value: factory(),
      timestamp: now,
      deps,
    }
  }

  return ref.current.value
}

/**
 * Hook for measuring component render performance.
 */
export function useRenderPerformance(componentName: string, enabled: boolean = false) {
  const renderCountRef = useRef(0)
  const startTimeRef = useRef<number>()

  useEffect(() => {
    if (!enabled) return

    renderCountRef.current += 1
    startTimeRef.current = performance.now()
  })

  useEffect(() => {
    if (!enabled || !startTimeRef.current) return

    const renderTime = performance.now() - startTimeRef.current

    if (renderTime > 16.67) { // More than one frame at 60fps
      console.warn(`${componentName} render took ${renderTime.toFixed(2)}ms (slow render)`)
    }

    return () => {
      if (startTimeRef.current) {
        const totalTime = performance.now() - startTimeRef.current
        console.debug(`${componentName} render #${renderCountRef.current}: ${totalTime.toFixed(2)}ms`)
      }
    }
  })
}

/**
 * Lazy loading utility for dynamic imports.
 */
export function lazyLoad<T extends React.ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ComponentType<any>
) {
  const LazyComponent = React.lazy(importFunc)

  return (props: React.ComponentProps<T>) => (
    React.createElement(
      React.Suspense,
      { fallback: fallback ? React.createElement(fallback) : null },
      React.createElement(LazyComponent, props)
    )
  )
}

/**
 * Intersection Observer hook for lazy loading content.
 */
export function useIntersectionObserver(
  ref: React.RefObject<Element>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = React.useState(false)
  const [hasIntersected, setHasIntersected] = React.useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting)
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true)
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    )

    observer.observe(element)

    return () => {
      observer.unobserve(element)
    }
  }, [ref, hasIntersected, options])

  return { isIntersecting, hasIntersected }
}

/**
 * Virtual scrolling hook for large lists.
 */
export function useVirtualScroll<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 5,
}: {
  items: T[]
  itemHeight: number
  containerHeight: number
  overscan?: number
}) {
  const [scrollTop, setScrollTop] = React.useState(0)

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  )

  const visibleItems = items.slice(startIndex, endIndex + 1)
  const totalHeight = items.length * itemHeight
  const offsetY = startIndex * itemHeight

  return {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll: (event: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(event.currentTarget.scrollTop)
    },
  }
}

/**
 * Service worker registration utility.
 */
export function registerServiceWorker() {
  if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then(registration => {
          console.log('SW registered: ', registration)
        })
        .catch(registrationError => {
          console.log('SW registration failed: ', registrationError)
        })
    })
  }
}

/**
 * Bundle size monitoring utility.
 */
export function logBundleSize() {
  if (process.env.NODE_ENV === 'development') {
    // Use dynamic import to avoid bundling in production
    import('webpack-bundle-analyzer').then(({ BundleAnalyzerPlugin }) => {
      console.log('Bundle analyzer available for development builds')
    }).catch(() => {
      console.log('Bundle analyzer not available')
    })
  }
}

/**
 * Performance monitoring hook.
 */
export function usePerformanceMonitor(name: string, enabled: boolean = false) {
  const startTimeRef = useRef<number>()

  useEffect(() => {
    if (!enabled) return

    startTimeRef.current = performance.now()
    console.time(name)
  })

  useEffect(() => {
    if (!enabled || !startTimeRef.current) return

    const duration = performance.now() - startTimeRef.current
    console.timeEnd(name)

    // Log slow operations
    if (duration > 100) {
      console.warn(`${name} took ${duration.toFixed(2)}ms (slow)`)
    }
  })
}