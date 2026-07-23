import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F5F8F6",
        surface: "#FFFFFF",
        sidebar: {
          DEFAULT: "#101F1B",
          active: "#17352B",
          text: "#9CAEA6",
        },
        border: {
          DEFAULT: "#E2E8E5",
          subtle: "#EDF1EE",
        },
        ink: {
          DEFAULT: "#16231F",
          secondary: "#5E6E68",
          muted: "#8B9994",
        },
        brand: {
          DEFAULT: "#0F6659",
          hover: "#0C544A",
          50: "#E1F5EE",
          800: "#085041",
        },
        success: { DEFAULT: "#2F9E6E", bg: "#E1F5EE", text: "#085041" },
        warning: { DEFAULT: "#E3A23D", bg: "#FAEEDA", text: "#633806" },
        danger: { DEFAULT: "#C1483B", bg: "#FCEBEB", text: "#791F1F" },
      },
      fontFamily: {
        display: ["var(--font-sora)", "sans-serif"],
        sans: ["var(--font-plex-sans)", "sans-serif"],
        mono: ["var(--font-plex-mono)", "monospace"],
      },
      borderRadius: {
        card: "12px",
      },
    },
  },
  plugins: [],
};

export default config;
