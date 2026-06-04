/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#f8fafc",
        sage: "#dcfce7",
        mint: "#10b981",
        sand: "#fef3c7",
        coral: "#fb7185"
      },
      boxShadow: {
        float: "0 20px 40px rgba(15, 23, 42, 0.12)"
      }
    }
  },
  plugins: []
};

