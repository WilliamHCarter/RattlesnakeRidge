/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
      },
      boxShadow: {
        'ctr2xl': '0 0px 45px -12px rgb(0 0 0 / 0.45)',
      },
      colors : {
        neutral: "#f4f4f4",
      },
      screens: {
        'pc': '1024px',
      },
    },

  },
  plugins: [],
};
