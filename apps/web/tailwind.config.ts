import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202A",
        mist: "#F5F7FA",
        signal: "#0E7C7B",
        accent: "#C7822B"
      }
    }
  },
  plugins: []
};

export default config;
