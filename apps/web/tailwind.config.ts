import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#e0f2fe",
        paper: "#0f172a",
        line: "#1e3a5f",
        pine: "#22d3ee",
        cobalt: "#818cf8",
        coral: "#fb7185"
      }
    }
  },
  plugins: []
};

export default config;
