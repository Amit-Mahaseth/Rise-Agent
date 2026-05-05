/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        hot: { DEFAULT: '#ef4444', light: '#fca5a5' },
        warm: { DEFAULT: '#facc15', light: '#fde68a' },
        cold: { DEFAULT: '#60a5fa', light: '#bfdbfe' },
        surface: {
          950: '#030712',
          900: '#111827',
          800: '#1f2937',
          700: '#374151',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
