/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        category: {
          ptqWeightOnly:        '#4A90D9',
          ptqWeightActivation:  '#E87D3E',
          qat:                  '#7B68EE',
          extremeLowbit:        '#E84393',
          kvCache:              '#3DAD78',
          lowPrecisionTraining: '#D4A027',
          moe:                  '#9B59B6',
          systems:              '#607D8B',
        },
      },
      fontFamily: {
        sans: [
          'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"',
          'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', '"Helvetica Neue"',
          'Arial', 'sans-serif',
        ],
        mono: [
          'ui-monospace', 'SFMono-Regular', '"SF Mono"', 'Consolas',
          '"Liberation Mono"', 'Menlo', 'monospace',
        ],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
