import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#09090B",
          surface: "#0F1115",
          elevated: "#151821",
          card: "rgba(20,24,32,0.78)",
          border: "rgba(255,255,255,0.08)",
        },
        foreground: {
          DEFAULT: "#F8FAFC",
          muted: "#CBD5E1",
          subtle: "#64748B",
          disabled: "#475569",
        },
        accent: {
          DEFAULT: "#38BDF8",
          muted: "#075985",
          subtle: "#7DD3FC",
        },
        violet: {
          DEFAULT: "#8B5CF6",
          muted: "#4C1D95",
          subtle: "#C4B5FD",
        },
        success: {
          DEFAULT: "#22C55E",
          muted: "#166534",
        },
        warning: {
          DEFAULT: "#F59E0B",
          muted: "#92400E",
        },
        error: {
          DEFAULT: "#FB7185",
          muted: "#9F1239",
        },
      },
      spacing: {
        // Premium spacing scale
        'xs': '0.25rem',
        'sm': '0.5rem',
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '3rem',
        '3xl': '4rem',
      },
      borderRadius: {
        // Consistent border radius
        'sm': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem',
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
        'medium': '0 12px 40px -24px rgba(56, 189, 248, 0.45)',
        'large': '0 24px 80px -40px rgba(139, 92, 246, 0.55)',
        'glow': '0 0 32px rgba(56, 189, 248, 0.16)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
