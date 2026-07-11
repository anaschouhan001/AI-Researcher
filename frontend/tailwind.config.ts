import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-quicksand)", "system-ui", "sans-serif"],
        cute: ["var(--font-pacifico)", "cursive"],
      },
      colors: {
        surface: {
          DEFAULT: "#fff0f6",
          raised: "#ffffff",
          overlay: "#ffe3ee",
        },
        blush: {
          50: "#fff5f9",
          100: "#ffe3ee",
          200: "#ffc6dd",
          300: "#ff9ec4",
          400: "#ff6fa5",
          500: "#f9498c",
          600: "#e02f75",
          700: "#bd1e5e",
          800: "#9a1a4e",
          900: "#7d1a43",
        },
      },
      boxShadow: {
        candy: "0 4px 20px -2px rgba(249, 73, 140, 0.25)",
        "candy-lg": "0 10px 40px -4px rgba(249, 73, 140, 0.35)",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "float-slow": {
          "0%, 100%": { transform: "translateY(0) rotate(-3deg)" },
          "50%": { transform: "translateY(-16px) rotate(3deg)" },
        },
        heartbeat: {
          "0%, 100%": { transform: "scale(1)" },
          "10%": { transform: "scale(1.15)" },
          "20%": { transform: "scale(1)" },
          "30%": { transform: "scale(1.1)" },
          "40%": { transform: "scale(1)" },
        },
        sparkle: {
          "0%, 100%": { opacity: "0.3", transform: "scale(0.8) rotate(0deg)" },
          "50%": { opacity: "1", transform: "scale(1.15) rotate(15deg)" },
        },
        wiggle: {
          "0%, 100%": { transform: "rotate(-3deg)" },
          "50%": { transform: "rotate(3deg)" },
        },
        "gradient-x": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        "bounce-soft": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.6s linear infinite",
        "fade-in": "fade-in 0.3s ease-out both",
        float: "float 4s ease-in-out infinite",
        "float-slow": "float-slow 7s ease-in-out infinite",
        heartbeat: "heartbeat 2.2s ease-in-out infinite",
        sparkle: "sparkle 2.4s ease-in-out infinite",
        wiggle: "wiggle 1.2s ease-in-out infinite",
        "gradient-x": "gradient-x 8s ease infinite",
        "bounce-soft": "bounce-soft 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
