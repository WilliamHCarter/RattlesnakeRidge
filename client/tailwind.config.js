/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      boxShadow: {
        'ctr2xl': '0 0px 45px -12px rgb(0 0 0 / 0.45)',
      },
      colors: {
        neutral: '#f4f4f4',
        dneutral: '#1f1f1f',
        lbg: '#ffffff',
        dbg: '#09090b',
        button: '#f4f4f4',
        dbutton: '#27272a',
        border: 'hsl(240 5.9% 90%)',
        dborder: 'hsl(240 3.7% 15.9%)',
      },
      screens: {
        'pc': '1300px',
        'laptop': '1024px',
        'tablet': '600px',
      },
      placeholderColor: theme => ({
        ...theme('colors'),
        'green-600': theme('colors.green.600'),
      }),
    },

  },
  variants: {
    extend: {
      // Enable the placeholder color variant for placeholders
      placeholderColor:
          [
            'responsive', 'dark', 'group-hover', 'focus-within', 'hover',
            'focus'
          ],
    },
  },
  plugins: [],
  darkMode: 'class',

};
