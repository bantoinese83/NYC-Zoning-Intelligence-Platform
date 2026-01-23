#!/usr/bin/env node

/**
 * Development Tools for NYC Zoning Intelligence Platform
 *
 * This script provides various development utilities and shortcuts
 * to improve the developer experience.
 */

const { execSync, spawn } = require('child_process')
const fs = require('fs')
const path = require('path')

const commands = {
  setup: () => {
    console.log('🚀 Setting up development environment...')

    // Install dependencies
    execSync('npm install', { stdio: 'inherit' })

    // Setup husky
    execSync('npx husky install', { stdio: 'inherit' })

    // Setup pre-commit hooks
    execSync('npx husky add .husky/pre-commit "npx lint-staged"', { stdio: 'inherit' })

    console.log('✅ Development environment setup complete!')
  },

  dev: () => {
    console.log('🚀 Starting development server with turbo...')
    spawn('npm', ['run', 'dev'], {
      stdio: 'inherit',
      shell: true,
    })
  },

  build: () => {
    console.log('🔨 Building for production...')
    execSync('npm run build', { stdio: 'inherit' })
  },

  'build:analyze': () => {
    console.log('📊 Analyzing bundle size...')
    execSync('npm run build:analyze', { stdio: 'inherit' })
  },

  test: () => {
    console.log('🧪 Running tests...')
    execSync('npm test', { stdio: 'inherit' })
  },

  'test:watch': () => {
    console.log('👀 Running tests in watch mode...')
    spawn('npm', ['run', 'test:watch'], {
      stdio: 'inherit',
      shell: true,
    })
  },

  'test:coverage': () => {
    console.log('📈 Generating test coverage report...')
    execSync('npm run test:coverage', { stdio: 'inherit' })
  },

  lint: () => {
    console.log('🔍 Running linter...')
    execSync('npm run lint', { stdio: 'inherit' })
  },

  'lint:fix': () => {
    console.log('🔧 Auto-fixing linting issues...')
    execSync('npm run lint:fix', { stdio: 'inherit' })
  },

  format: () => {
    console.log('💅 Formatting code...')
    execSync('npx prettier --write .', { stdio: 'inherit' })
  },

  typecheck: () => {
    console.log('🔍 Running TypeScript type checking...')
    execSync('npm run type-check', { stdio: 'inherit' })
  },

  clean: () => {
    console.log('🧹 Cleaning build artifacts...')
    execSync('npm run clean', { stdio: 'inherit' })
  },

  storybook: () => {
    console.log('📚 Starting Storybook...')
    spawn('npm', ['run', 'storybook'], {
      stdio: 'inherit',
      shell: true,
    })
  },

  quality: () => {
    console.log('🎯 Running full quality check...')
    try {
      execSync('npm run type-check', { stdio: 'inherit' })
      execSync('npm run lint', { stdio: 'inherit' })
      execSync('npm run test:coverage', { stdio: 'inherit' })
      console.log('✅ All quality checks passed!')
    } catch (error) {
      console.error('❌ Quality checks failed:', error.message)
      process.exit(1)
    }
  },

  'deps:check': () => {
    console.log('📦 Checking for outdated dependencies...')
    execSync('npm outdated', { stdio: 'inherit' })
  },

  'deps:update': () => {
    console.log('⬆️ Updating dependencies...')
    execSync('npm update', { stdio: 'inherit' })
  },

  size: () => {
    console.log('📏 Analyzing bundle size...')
    execSync('npx webpack-bundle-analyzer .next/static/chunks/*.js', { stdio: 'inherit' })
  },

  'performance:monitor': () => {
    console.log('📊 Starting performance monitoring...')
    // This would integrate with performance monitoring tools
    console.log('Performance monitoring not yet implemented')
  },

  help: () => {
    console.log(`
🛠️  NYC Zoning Intelligence Platform - Development Tools

Usage: node dev-tools.js <command>

Available commands:
  setup                - Initial development environment setup
  dev                  - Start development server with turbo
  build               - Build for production
  build:analyze       - Analyze bundle size
  test                - Run tests once
  test:watch          - Run tests in watch mode
  test:coverage       - Generate test coverage
  lint                - Run linter
  lint:fix            - Auto-fix linting issues
  format              - Format code with Prettier
  typecheck           - Run TypeScript checking
  clean               - Clean build artifacts
  storybook           - Start Storybook
  quality             - Run all quality checks
  deps:check          - Check for outdated dependencies
  deps:update         - Update dependencies
  size                - Analyze bundle size
  performance:monitor - Start performance monitoring
  help                - Show this help message

Examples:
  node dev-tools.js setup
  node dev-tools.js dev
  node dev-tools.js quality
  node dev-tools.js test:coverage
`)
  }
}

const command = process.argv[2]

if (!command) {
  console.log('❌ No command specified')
  commands.help()
  process.exit(1)
}

if (commands[command]) {
  try {
    commands[command]()
  } catch (error) {
    console.error(`❌ Command "${command}" failed:`, error.message)
    process.exit(1)
  }
} else {
  console.log(`❌ Unknown command: ${command}`)
  commands.help()
  process.exit(1)
}