/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#1e1b4b",
        },
        accent: {
          50: "#ecfeff",
          100: "#cffafe",
          200: "#a5f3fc",
          500: "#06b6d4",
          600: "#0891b2",
        },
        grape: {
          50: "#faf5ff",
          100: "#f3e8ff",
          500: "#a855f7",
          600: "#9333ea",
        },
        candy: {
          50: "#fdf2f8",
          100: "#fce7f3",
          500: "#ec4899",
          600: "#db2777",
        },
        success: "#10b981",
        warning: "#f59e0b",
        danger: "#ef4444",
        info: "#3b82f6",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      boxShadow: {
        soft: "0 12px 30px rgba(15, 23, 42, 0.08)",
        panel: "0 24px 70px rgba(15, 23, 42, 0.10)",
        glow: "0 18px 55px rgba(79, 70, 229, 0.22)",
        "glow-violet": "0 16px 40px -12px rgba(139, 92, 246, 0.55)",
        "glow-pink": "0 16px 40px -12px rgba(236, 72, 153, 0.5)",
        "glow-teal": "0 16px 40px -12px rgba(20, 184, 166, 0.5)",
        "glow-amber": "0 16px 40px -12px rgba(245, 158, 11, 0.5)",
        "glow-rose": "0 16px 40px -12px rgba(244, 63, 94, 0.5)",
        insetSoft: "inset 0 1px 0 rgba(255,255,255,.65)",
      },
      backgroundImage: {
        aurora:
          "radial-gradient(circle at 8% -8%, rgba(139,92,246,0.20), transparent 34rem), radial-gradient(circle at 92% 4%, rgba(236,72,153,0.16), transparent 30rem), radial-gradient(circle at 55% 120%, rgba(6,182,212,0.16), transparent 34rem)",
      },
      animation: {
        "fade-in": "fadeIn 0.25s ease-out",
        "slide-up": "slideUp 0.32s ease-out",
        sheen: "sheen 2.6s linear infinite",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: 0 }, "100%": { opacity: 1 } },
        slideUp: {
          "0%": { opacity: 0, transform: "translateY(14px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        sheen: {
          "0%": { backgroundPosition: "200% center" },
          "100%": { backgroundPosition: "-200% center" },
        },
      },
    },
  },
  plugins: [],
};
