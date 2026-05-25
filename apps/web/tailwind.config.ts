import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Monochromatic grayscale palette
        background: {
          DEFAULT: "#000000",
          surface: "#0a0a0a",
          elevated: "#111111",
          card: "#161616",
          border: "#262626",
        },
        foreground: {
          DEFAULT: "#ffffff",
          muted: "#a3a3a3",
          subtle: "#737373",
          disabled: "#525252",
        },
        // Single subtle AI accent (muted electric blue)
        accent: {
          DEFAULT: "#3b82f6",
          muted: "#1e40af",
          subtle: "#60a5fa",
        },
        // Semantic colors (minimal, muted)
        success: {
          DEFAULT: "#22c55e",
          muted: "#166534",
        },
        warning: {
          DEFAULT: "#eab308",
          muted: "#a16207",
        },
        error: {
          DEFAULT: "#ef4444",
          muted: "#991b1b",
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
        'sm': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        // Subtle shadows
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'large': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
