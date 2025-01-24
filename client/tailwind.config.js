/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    screens: {
      sm: '640px',
      md: '768px',
      ml: '896px',
      lg: '1024px',
      xl: '1280px',
    },
    extend: {
      fontSize: {
        'headline1': ['56px', { lineHeight: '64px', fontWeight: '800' }],
        'headline2': ['48px', { lineHeight: '56px', fontWeight: '700' }],
        'headline3': ['40px', { lineHeight: '48px', fontWeight: '600' }],
        'headline4': ['32px', { lineHeight: '40px', fontWeight: '500' }],
        'subtitle1': ['24px', { lineHeight: '32px', fontWeight: '400' }],
      },
      colors: {
        customFg: '#2B3139',
        customBlue: '#4B9CD3',
        customGreen: '#A8D08D',
        gray: {
          1200: '#24292E',
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

