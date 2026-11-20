/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        frame: '#F5F5F5',
        ink: '#0A0A0A',
        muted: '#8A8F98',
        lime: {
          DEFAULT: '#CBFF97',
          deep: '#B7EE7C',
        },
        peri: {
          DEFAULT: '#B3C4F5',
          deep: '#6F86E8',
        },
        forest: '#0D6543',
        air: '#0369A1',
        sampah: '#6B7280',
        alsintan: '#A16207',
      },
      borderRadius: {
        card: '20px',
        frame: '32px',
      },
      fontFamily: {
        sans: ['Albert Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
