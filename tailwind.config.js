/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './frontend/src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Outfit', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
      colors: {
        deep: '#0D0B0E',
        main: '#13111A',
        card: '#1A1720',
        'card-hover': '#221F2A',
        bdr: '#2A2530',
        'bdr-light': '#3A3540',
        txt: '#F5F0EB',
        muted: '#8B8494',
        dim: '#5A5464',
        amber: {
          DEFAULT: '#F59E0B',
          hover: '#D97706',
          glow: 'rgba(245,158,11,0.3)',
          soft: 'rgba(245,158,11,0.08)',
        },
        rose: {
          DEFAULT: '#E11D48',
          glow: 'rgba(225,29,72,0.3)',
        },
        emerald: {
          DEFAULT: '#10B981',
          glow: 'rgba(16,185,129,0.3)',
        },
      },
    },
  },
  plugins: [],
};