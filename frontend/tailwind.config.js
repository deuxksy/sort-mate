/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#22c55e",
          dark: "#16a34a",
          darker: "#166534",
        },
        eco: {
          bg: "#f0faf0",
          surface: "#ffffff",
        },
      },
    },
  },
  plugins: [],
};
