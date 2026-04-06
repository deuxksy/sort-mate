/** @type {import('tailwindcss').Config} */
const designTokens = require("./tailwind.tokens.js");

module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./stories/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        ...designTokens.color,
      },
      ...(designTokens.spacing ? { spacing: designTokens.spacing } : {}),
      ...(designTokens.borderRadius ? { borderRadius: designTokens.borderRadius } : {}),
    },
  },
  plugins: [],
};
