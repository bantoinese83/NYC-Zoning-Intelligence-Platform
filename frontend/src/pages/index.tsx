'use client'

import { useRouter } from 'next/router'
import { useState, useEffect } from 'react'
import Head from 'next/head'
import { PropertySearch } from '@/components/PropertySearch'
import { PropertyMap } from '@/components/PropertyMap'
import { MapLegend } from '@/components/MapLegend'
import { useStats } from '@/hooks/useStats'
import { ErrorBoundary, ErrorFallback } from '@/components/ErrorBoundary'
import { Property } from '@/types'
import { Building, MapPin, FileText, TrendingUp, Search, CheckCircle, Star, Users, Award, Zap, Shield, BarChart3, Globe, Target, Building2, Lightbulb } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch real-time platform stats
  const { data: stats, isLoading: statsLoading, error: statsError } = useStats()

  // Handle URL search parameters
  useEffect(() => {
    const { search } = router.query
    if (search && typeof search === 'string') {
      setSearchQuery(search)
    }
  }, [router.query])

  const handlePropertySelect = (property: Property) => {
    // Navigate to analysis page with property ID
    router.push(`/analysis?propertyId=${property.id}`)
  }

  const handlePopularAreaClick = (areaName: string, neighborhood?: string) => {
    // Set the search query directly
    const query = neighborhood ? `${neighborhood}, ${areaName}` : areaName
    setSearchQuery(query)
  }

  // Format numbers for display
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M+`
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K+`
    } else {
      return num.toString()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <Head>
          <title>NYC Zoning Intelligence - Smart Property Analysis for Real Estate Professionals</title>
          <meta
            name="description"
            content="Unlock NYC property potential with AI-powered zoning analysis, tax incentives, and comprehensive market intelligence. Make data-driven real estate decisions."
          />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <meta name="keywords" content="NYC zoning, property analysis, tax incentives, real estate, Manhattan, Brooklyn, Queens" />
          <link rel="icon" href="/logo.svg" />
        </Head>

        {/* Navigation */}
        <nav className="bg-white/80 backdrop-blur-md border-b border-white/20 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                  <Building className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    NYC Zoning Pro
                  </h1>
                  <p className="text-xs text-gray-500 hidden sm:block">
                    Smart Property Intelligence
                  </p>
                </div>
              </div>
              <div className="hidden md:flex items-center space-x-6">
                <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
                <a href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors">How It Works</a>
                <button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all duration-200">
                  Get Started
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="text-center mb-20">
            {/* Trust Indicators */}
            <div className="flex justify-center items-center space-x-6 mb-8 opacity-70">
              <div className="flex items-center space-x-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm text-gray-600">Official NYC Data</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4 text-blue-600" />
                <span className="text-sm text-gray-600">10,000+ Properties</span>
              </div>
              <div className="flex items-center space-x-1">
                <Award className="h-4 w-4 text-purple-600" />
                <span className="text-sm text-gray-600">Industry Leading</span>
              </div>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Unlock NYC Property
              </span>
              <br />
              <span className="text-gray-800">Intelligence</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              Transform your real estate decisions with AI-powered zoning analysis, tax incentives,
              and comprehensive market intelligence. Make data-driven investments across all five boroughs.
            </p>

            {/* Key Benefits */}
            <div className="flex flex-wrap justify-center gap-4 mb-10">
              <div className="bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm flex items-center space-x-2">
                <Zap className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">Instant Analysis</span>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm flex items-center space-x-2">
                <Target className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-gray-700">100% Accurate</span>
              </div>
              <div className="bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium text-gray-700">Maximize ROI</span>
              </div>
            </div>

            {/* Enhanced Search Bar */}
            <div className="max-w-2xl mx-auto mb-8">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-2">
                <ErrorBoundary
                  fallback={
                    <ErrorFallback
                      title="Search Unavailable"
                      message="The property search is temporarily unavailable. Please try again later."
                    />
                  }
                >
                  <PropertySearch
                    onPropertySelect={handlePropertySelect}
                    placeholder="Enter any NYC address (e.g., '123 Broadway' or 'Williamsburg, Brooklyn')"
                    className="w-full"
                    initialQuery={searchQuery}
                  />
                </ErrorBoundary>
              </div>
              <p className="text-sm text-gray-500 mt-3">
                Search by address, neighborhood, or borough • No signup required
              </p>
            </div>

            {/* Quick Actions */}
            <div className="flex flex-wrap justify-center gap-3">
              <button
                onClick={() => handlePopularAreaClick('Manhattan', 'Financial District')}
                className="bg-white/80 backdrop-blur-sm hover:bg-white text-gray-700 px-4 py-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 flex items-center space-x-2"
              >
                <MapPin className="h-4 w-4" />
                <span>Financial District</span>
              </button>
              <button
                onClick={() => handlePopularAreaClick('Brooklyn', 'Williamsburg')}
                className="bg-white/80 backdrop-blur-sm hover:bg-white text-gray-700 px-4 py-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 flex items-center space-x-2"
              >
                <MapPin className="h-4 w-4" />
                <span>Williamsburg</span>
              </button>
              <button
                onClick={() => handlePopularAreaClick('Queens', 'Long Island City')}
                className="bg-white/80 backdrop-blur-sm hover:bg-white text-gray-700 px-4 py-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 flex items-center space-x-2"
              >
                <MapPin className="h-4 w-4" />
                <span>Long Island City</span>
              </button>
            </div>
          </div>

          {/* Features Grid */}
          <div id="features" className="mb-20">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Everything You Need for Smart Investing
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Comprehensive property intelligence powered by official NYC data sources
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl p-8 text-center transform hover:-translate-y-2 transition-all duration-300 border border-white/50">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <Building className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  Zoning Analysis
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Detailed FAR calculations, setback requirements, height limits, and building restrictions for maximum development potential.
                </p>
                <div className="mt-4 flex justify-center">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    <Zap className="w-3 h-3 mr-1" />
                    AI-Powered
                  </span>
                </div>
              </div>

              <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl p-8 text-center transform hover:-translate-y-2 transition-all duration-300 border border-white/50">
                <div className="bg-gradient-to-br from-green-500 to-green-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <TrendingUp className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  Tax Incentives
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Check eligibility for 467-M, ICAP, 421-a, and 50+ other NYC tax abatement programs to maximize your savings.
                </p>
                <div className="mt-4 flex justify-center">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <BarChart3 className="w-3 h-3 mr-1" />
                    $Millions Saved
                  </span>
                </div>
              </div>

              <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl p-8 text-center transform hover:-translate-y-2 transition-all duration-300 border border-white/50">
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <MapPin className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  Landmark Intelligence
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Discover nearby historic, cultural, and natural landmarks within 150 feet that could impact your development plans.
                </p>
                <div className="mt-4 flex justify-center">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                    <Globe className="w-3 h-3 mr-1" />
                    Historic Data
                  </span>
                </div>
              </div>

              <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl p-8 text-center transform hover:-translate-y-2 transition-all duration-300 border border-white/50">
                <div className="bg-gradient-to-br from-orange-500 to-orange-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <FileText className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  Professional Reports
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Generate comprehensive PDF reports with interactive maps, zoning analysis, and investment recommendations.
                </p>
                <div className="mt-4 flex justify-center">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                    <Shield className="w-3 h-3 mr-1" />
                    Bank-Ready
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Map Section */}
          <div className="mb-20">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Explore Every Corner of NYC
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Interactive zoning map covering all five boroughs with real-time property intelligence
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl overflow-hidden border border-white/50">
              <div className="p-8 border-b border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">
                      Live Zoning Map
                    </h3>
                    <p className="text-gray-600 mt-1">
                      Click any property to instantly analyze zoning, FAR, and development potential
                    </p>
                  </div>
                  <div className="hidden md:flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Residential</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Commercial</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Mixed-Use</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="h-96 md:h-[500px]">
                <ErrorBoundary
                  fallback={
                    <div className="w-full h-full flex items-center justify-center bg-gray-50 rounded-b-3xl">
                      <ErrorFallback
                        title="Map Unavailable"
                        message="The interactive map is temporarily unavailable. Please try refreshing the page."
                      />
                    </div>
                  }
                >
                  <PropertyMap showControls={true} />
                </ErrorBoundary>
              </div>

              {/* Map Legend */}
              <MapLegend />
            </div>
          </div>

          {/* How It Works Section */}
          <div id="how-it-works" className="mb-20">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                How It Works
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Get comprehensive property intelligence in three simple steps
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Search className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">1. Search Property</h3>
                <p className="text-gray-600 leading-relaxed">
                  Enter any NYC address or browse popular neighborhoods. Our AI instantly finds and analyzes the property.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-green-500 to-green-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Zap className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">2. AI Analysis</h3>
                <p className="text-gray-600 leading-relaxed">
                  Advanced algorithms process zoning codes, tax incentives, landmarks, and market data for comprehensive insights.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <FileText className="h-10 w-10 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">3. Make Decisions</h3>
                <p className="text-gray-600 leading-relaxed">
                  Get actionable recommendations, download professional reports, and maximize your real estate investments.
                </p>
              </div>
            </div>
          </div>

          {/* Popular Areas & Quick Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
            {/* Popular Areas */}
            <div className="lg:col-span-2">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-8 border border-white/50">
                <div className="flex items-center space-x-3 mb-6">
                  <Building2 className="h-6 w-6 text-blue-600" />
                  <h3 className="text-2xl font-bold text-gray-900">Popular Investment Areas</h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <button
                    onClick={() => handlePopularAreaClick('Manhattan', 'Financial District')}
                    className="group p-4 rounded-xl border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 text-left"
                  >
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-5 w-5 text-blue-600 mt-0.5 group-hover:scale-110 transition-transform" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Financial District</h4>
                        <p className="text-sm text-gray-600">Prime Manhattan location with high development potential</p>
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={() => handlePopularAreaClick('Brooklyn', 'Williamsburg')}
                    className="group p-4 rounded-xl border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-all duration-200 text-left"
                  >
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-5 w-5 text-green-600 mt-0.5 group-hover:scale-110 transition-transform" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Williamsburg</h4>
                        <p className="text-sm text-gray-600">Trending Brooklyn neighborhood with creative energy</p>
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={() => handlePopularAreaClick('Queens', 'Long Island City')}
                    className="group p-4 rounded-xl border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all duration-200 text-left"
                  >
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-5 w-5 text-purple-600 mt-0.5 group-hover:scale-110 transition-transform" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Long Island City</h4>
                        <p className="text-sm text-gray-600">Queens tech hub with modern office developments</p>
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={() => handlePopularAreaClick('Manhattan', 'Chelsea')}
                    className="group p-4 rounded-xl border border-gray-200 hover:border-pink-300 hover:bg-pink-50 transition-all duration-200 text-left"
                  >
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-5 w-5 text-pink-600 mt-0.5 group-hover:scale-110 transition-transform" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Chelsea</h4>
                        <p className="text-sm text-gray-600">Historic Manhattan district with luxury condos</p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            {/* Stats Sidebar */}
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
                <div className="flex items-center space-x-3 mb-4">
                  <Star className="h-6 w-6" />
                  <h4 className="text-lg font-bold">Platform Stats</h4>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-blue-100">Properties Analyzed</span>
                    <span className="font-bold">
                      {statsLoading ? (
                        <div className="animate-pulse bg-blue-200/30 rounded h-6 w-16"></div>
                      ) : statsError ? (
                        '0'
                      ) : (
                        formatNumber(stats?.properties_analyzed || 0)
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-100">Tax Programs</span>
                    <span className="font-bold">
                      {statsLoading ? (
                        <div className="animate-pulse bg-blue-200/30 rounded h-6 w-12"></div>
                      ) : statsError ? (
                        '0'
                      ) : (
                        stats?.tax_programs || 0
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-100">Zoning Districts</span>
                    <span className="font-bold">
                      {statsLoading ? (
                        <div className="animate-pulse bg-blue-200/30 rounded h-6 w-12"></div>
                      ) : statsError ? (
                        '0'
                      ) : (
                        stats?.zoning_districts || 0
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-blue-100">Data Accuracy</span>
                    <span className="font-bold">
                      {stats?.data_accuracy || 100}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-white/50">
                <div className="flex items-center space-x-2 mb-4">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  <h4 className="font-bold text-gray-900">Pro Tips</h4>
                </div>
                <ul className="space-y-3 text-sm text-gray-600">
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Check FAR ratios before purchasing land</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Tax incentives can save millions on large developments</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Historic districts have strict preservation rules</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
              {/* Brand */}
              <div className="md:col-span-2">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                    <Building className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">NYC Zoning Pro</h3>
                    <p className="text-sm text-gray-400">Smart Property Intelligence</p>
                  </div>
                </div>
                <p className="text-gray-300 mb-4 max-w-md">
                  Empowering real estate professionals with AI-powered zoning analysis,
                  tax incentives, and comprehensive market intelligence for New York City.
                </p>
                <div className="flex space-x-4">
                  <button className="text-gray-400 hover:text-white transition-colors">
                    <span className="sr-only">Twitter</span>
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                    </svg>
                  </button>
                  <button className="text-gray-400 hover:text-white transition-colors">
                    <span className="sr-only">LinkedIn</span>
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </button>
                </div>
              </div>

              {/* Quick Links */}
              <div>
                <h4 className="text-sm font-semibold text-white mb-4">Platform</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                  <li><a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">API Docs</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                </ul>
              </div>

              {/* Resources */}
              <div>
                <h4 className="text-sm font-semibold text-white mb-4">Resources</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">NYC Zoning Codes</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Tax Incentive Guide</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Market Reports</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                </ul>
              </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-gray-800 pt-8">
              <div className="flex flex-col md:flex-row justify-between items-center">
                <div className="text-sm text-gray-400 mb-4 md:mb-0">
                  <p>&copy; 2026 NYC Zoning Pro. Built with official NYC Open Data.</p>
                  <p className="mt-1">
                    This tool is for informational purposes only. Always consult with qualified professionals
                    for legal and financial advice.
                  </p>
                </div>
                <div className="flex space-x-6 text-sm text-gray-400">
                  <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                  <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                  <a href="#" className="hover:text-white transition-colors">Contact</a>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
  )
}