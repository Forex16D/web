/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {
      colors: {
        customFg: '#2B3139',
        customBlue: '#4B9CD3',    // Define custom color for blue
        customGreen: '#A8D08D',   // Define custom color for green
      },
    },
  },
  plugins: [require('tailwindcss-primeui')]
}

