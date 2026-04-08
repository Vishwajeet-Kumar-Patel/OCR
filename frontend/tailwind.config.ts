import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#f7f6f2",
        ink: "#1e2320",
        accent: "#156b5a",
        warm: "#f1d9a7"
      },
      boxShadow: {
        card: "0 12px 30px rgba(0, 0, 0, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
