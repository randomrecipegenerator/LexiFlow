/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f3f8',
          100: '#d9e0ed',
          200: '#b3c1db',
          300: '#8da2c9',
          400: '#6683b7',
          500: '#4064a5',
          600: '#2a4a7a',
          700: '#1a3a5c',
          800: '#0f2740',
          900: '#0a1a2e',
          DEFAULT: '#0f172a',
        },
        gold: {
          50: '#fdf8e8',
          100: '#f9edc4',
          200: '#f0d98a',
          300: '#e2c96e',
          400: '#d4b94e',
          500: '#c9a84c',
          600: '#a88a30',
          700: '#8a6e24',
          800: '#6c541c',
          900: '#4e3c14',
          DEFAULT: '#c9a84c',
        },
        surface: {
          DEFAULT: '#0f172a',
          light: '#1e293b',
          lighter: '#334155',
          card: '#1e293b',
          border: '#334155',
        },
        text: {
          primary: '#f1f5f9',
          secondary: '#94a3b8',
          muted: '#64748b',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
        mono: ['SF Mono', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}