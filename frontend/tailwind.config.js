/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // kebab-case keys (used as text-apple-blue, bg-bg-gray, etc.)
        'apple-blue': '#0071e3',
        'bg-gray': '#f5f5f7',
        'text-primary': '#1d1d1f',
        'text-secondary': '#86868b',
        // camelCase aliases for convenience
        appleBlue: '#0071e3',
        bgGray: '#f5f5f7',
        textPrimary: '#1d1d1f',
        textSecondary: '#86868b',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Display"',
          '"Helvetica Neue"',
          'sans-serif',
        ],
      },
      borderRadius: {
        card: '16px',
        btn: '8px',
      },
      boxShadow: {
        card: '0 4px 20px rgba(0,0,0,0.05)',
      },
      backdropBlur: {
        glass: '20px',
      },
    },
  },
  plugins: [],
}
