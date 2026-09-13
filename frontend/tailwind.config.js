/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        primary: {
          50: '#F0FFD6',
          100: '#DFFFAA',
          200: '#C8FF6B',
          300: '#AAFF00',
          400: '#96E800',
          500: '#7FCC00',
          600: '#6BAF00',
          700: '#558C00',
          800: '#3E6600',
          900: '#264000',
        },

        surface: {
          50: '#0A0A0A',
          100: '#111111',
          200: '#1A1A1A',
          300: '#252525',
          400: '#333333',
          500: '#444444',
        },

        charcoal: {
          DEFAULT: '#F0F0F0',
          secondary: '#A0A0A0',
          muted: '#666666',
        },

        risk: {
          high: '#FF453A',
          'high-bg': '#2A1010',
          'high-border': '#5C1A1A',

          medium: '#FFB340',
          'medium-bg': '#2A210F',
          'medium-border': '#5C4518',

          low: '#30D158',
          'low-bg': '#102A18',
          'low-border': '#1E5C32',

          pass: '#A1A1AA',
          'pass-bg': '#181818',
          'pass-border': '#303030',
        },
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.6)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.6)',
        glow: '0 0 20px rgba(170,255,0,0.15)',
        'glow-strong': '0 0 30px rgba(170,255,0,0.25)',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        shimmer: 'shimmer 2s infinite linear',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-8px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
};