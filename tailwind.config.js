/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        fadeIn: 'fadeIn 0.10s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      backgroundImage: {
        bannerImg: "url('/images2.jpg')",
      },

      fontFamily: {
        noto: ["noto", "sans-serif"],
      },
    },
    
  },
  
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
}
