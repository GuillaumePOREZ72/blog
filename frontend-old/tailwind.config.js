/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./index.html"],
  theme: {
    extend: {
      keyframes: {
        loaderDots1: {
          "0%" : { transform: 'scale(0)'},
          "100%": { transform: 'scale(1)'}
        },
        loaderDots2: {
          "0%" : { transform: 'translate(0,0)'},
          "100%": { transform: 'translate(24px,0)'}
        },
        loaderDots3: {
          "0%" : { transform: 'scale(1)'},
          "100%": { transform: 'scale(0)'}
        }
      },
      animation: {
        loaderDots1: 'loaderDots1 0.6s infinite cubic-bezier(0,1,1,0)',
        loaderDots2: 'loaderDots2 0.6s infinite cubic-bezier(0,1,1,0)',
        loaderDots3: 'loaderDots3 0.6s infinite cubic-bezier(0,1,1,0)',
      }
    },
  },
  plugins: [],
}

