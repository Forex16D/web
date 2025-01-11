/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    screens: {
      ml: '960px',
    },
    extend: {
      colors: {
        customFg: '#2B3139',
        customBlue: '#4B9CD3',
        customGreen: '#A8D08D',
        gray: {
          1000: '#2B3139',
          800: '#1f2937',
          600: '#4b5563',
        },
      },
      outlineWidth: {
        '1': '1px',
        '2': '2px',
      },
    },
  },
  plugins: [require('tailwindcss-primeui')]
}

