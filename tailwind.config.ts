import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0A0B0F",
        surface: "#111318",
        elevated: "#181C24",
        overlay: "#1E2330",
        border: "#252B3B",
        indigo: "#4F46E5",
        teal: "#0D9488",
        amber: "#F59E0B",
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
        xl: "24px",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
        display: ["Fraunces", "serif"],
      },
    },
  },
};

export default config;
