/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'rgba(var(--color-primary), 0.05)',
          100: 'rgba(var(--color-primary), 0.1)',
          200: 'rgba(var(--color-primary), 0.2)',
          300: 'rgba(var(--color-primary), 0.3)',
          400: 'rgba(var(--color-primary), 0.4)',
          500: 'rgba(var(--color-primary), 0.5)',
          600: 'rgba(var(--color-primary), 0.6)',
          700: 'rgba(var(--color-primary), 0.7)',
          800: 'rgba(var(--color-primary), 0.8)',
          900: 'rgba(var(--color-primary), 0.9)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 