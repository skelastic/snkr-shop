/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        nike: {
          black: '#111111',
          gray: '#757575',
          orange: '#FF6900'
        }
      },
      fontFamily: {
        'nike': ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'bounce-in': 'bounceIn 0.3s ease',
        'flash-gradient': 'flashGradient 3s ease infinite',
        'loading': 'loading 1.5s infinite',
        'strike-through': 'strikeThrough 0.3s ease forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '50%': { transform: 'scale(1.2)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        flashGradient: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        loading: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        strikeThrough: {
          'to': { transform: 'scaleX(1)' },
        }
      },
      transform: {
        'hover-lift': 'translateY(-4px)',
      },
      boxShadow: {
        'nike': '0 4px 16px rgba(0, 0, 0, 0.15)',
        'nike-heavy': '0 8px 32px rgba(0, 0, 0, 0.2)',
      }
    },
  },
  plugins: [],
}