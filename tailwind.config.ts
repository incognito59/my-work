import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", "ui-sans-serif", "sans-serif"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
      keyframes: {
        neonBreathe: {
          "0%, 100%": { boxShadow: "0 0 18px rgba(34, 211, 238, .08)" },
          "50%": { boxShadow: "0 0 28px rgba(34, 211, 238, .28), 0 0 60px rgba(168, 85, 247, .12)" },
        },
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        ticker: {
          from: { transform: "translateY(0)" },
          to: { transform: "translateY(-50%)" },
        },
      },
      animation: {
        "neon-breathe": "neonBreathe 3s ease-in-out infinite",
        scanline: "scanline 5s linear infinite",
        ticker: "ticker 18s linear infinite",
      },
    },
  },
  plugins: [
    ({ addUtilities }) => {
      addUtilities({
        ".crt-scanlines": {
          backgroundImage: "repeating-linear-gradient(to bottom, transparent 0, transparent 3px, rgba(255,255,255,.025) 4px)",
        },
      });
    },
  ],
};

export default config;
