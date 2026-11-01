import "./globals.css";
import { Inter } from "next/font/google";
import { Navbar } from "../components/Navbar";
import { Atmosphere } from "../components/Atmosphere";
import { AuthProvider } from "../components/AuthProvider";
const inter = Inter({ subsets: ["latin"], variable: "--font-geist" });
export const metadata = { title: "AERM AI — Skin clarity, made gentle", description: "A calm Phase 1 skin analysis companion." };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body className={inter.variable}><AuthProvider><Navbar /><div className="site-stage"><Atmosphere />{children}</div></AuthProvider></body></html>;
}
