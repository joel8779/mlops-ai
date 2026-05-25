import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Graphite enterprise palette
        background: {
          DEFAULT: "#111315",
          surface: "#15181B",
          elevated: "#1B1F24",
          card: "#20252B",
          border: "#2D333B",
        },
        foreground: {
          DEFAULT: "#F5F7FA",
          muted: "#C7CDD4",
          subtle: "#8B949E",
          disabled: "#6E7681",
        },
        // Single muted amber accent
        accent: {
          DEFAULT: "#D6A756",
          muted: "#8B7335",
          subtle: "#EBC585",
        },
        // Semantic colors (minimal, muted)
        success: {
          DEFAULT: "#3FB950",
          muted: "#238636",
        },
        warning: {
          DEFAULT: "#D29922",
          muted: "#9A6700",
        },
        error: {
          DEFAULT: "#F85149",
          muted: "#B62324",
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
        // Subtle shadows
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
        'large': '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
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
