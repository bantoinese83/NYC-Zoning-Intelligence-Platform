module.exports = {
  // TypeScript and JavaScript files
  '**/*.{ts,tsx,js,jsx}': [
    'prettier --write',
    'eslint --fix --max-warnings 0',
  ],

  // TypeScript type checking
  '**/*.{ts,tsx}': [
    'tsc --noEmit',
  ],

  // JSON and configuration files
  '**/*.{json,md,yml,yaml}': [
    'prettier --write',
  ],

  // CSS and styling files
  '**/*.{css,scss,sass}': [
    'prettier --write',
  ],
}