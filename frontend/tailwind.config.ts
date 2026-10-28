import type { Config } from "tailwindcss";
const config: Config = { content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"], theme: { extend: { colors: { ivory: "#F8F5EC", ink: "#18352A", forest: "#1E5A45", sage: "#DCE7D9", clay: "#B86543", mist: "#EFF2EA" }, fontFamily: { sans: ["var(--font-geist)", "Arial", "sans-serif"] }, boxShadow: { soft: "0 18px 50px rgba(24,53,42,.08)" } } }, plugins: [] };
export default config;
