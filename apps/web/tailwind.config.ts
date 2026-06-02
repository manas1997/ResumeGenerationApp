import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17201b",
        paper: "#fbfbf8",
        line: "#d8ddd4",
        pine: "#1f6f5b",
        cobalt: "#2453a6",
        coral: "#b9533f"
      }
    }
  },
  plugins: []
};

export default config;

