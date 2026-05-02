/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        beige: {
          50: '#fdfcfb',
          100: '#f8f6f3',
          200: '#f3ede5',
          300: '#e8dfd3',
          400: '#d9cbb8',
          500: '#c9b89a',
          600: '#b5a186',
          700: '#9a8670',
          800: '#7d6e5c',
          900: '#5f5447'
        },
        green: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d'
        }
      }
    }
  },
  plugins: [],
}

// Made with Bob
