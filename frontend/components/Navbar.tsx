"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Logo } from "./Logo";
import { useAuth } from "./AuthProvider";
export function Navbar() {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const { user, loading, setUser } = useAuth();
  const close = () => setOpen(false);
  return <header className="sticky top-0 z-30 border-b border-ink/10 bg-ivory/80 backdrop-blur-xl">
    <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
      <Link href="/" onClick={close} className="focus-ring rounded-xl"><Logo /></Link>
      <button type="button" onClick={() => setOpen((value) => !value)} className="focus-ring rounded-xl p-2 text-forest md:hidden" aria-label={open ? "Close navigation" : "Open navigation"}>{open ? <X size={21} /> : <Menu size={21} />}</button>
      <nav className={`${open ? "absolute left-4 right-4 top-[calc(100%+8px)] flex" : "hidden"} glass-panel flex-col gap-1 rounded-2xl p-3 text-sm font-medium text-ink/70 md:static md:flex md:flex-row md:items-center md:gap-1 md:border-0 md:bg-transparent md:p-0 md:shadow-none`}>
        <Link onClick={close} className={`focus-ring rounded-full px-4 py-2 transition hover:bg-sage/70 ${path === "/routine" ? "bg-sage text-ink" : ""}`} href="/routine">Routine</Link>
        <Link onClick={close} className={`focus-ring rounded-full px-4 py-2 transition hover:bg-sage/70 ${path === "/products" ? "bg-sage text-ink" : ""}`} href="/products">Products</Link>
        {!loading && user && <Link onClick={close} className={`focus-ring rounded-full px-4 py-2 transition hover:bg-sage/70 ${path === "/profile" ? "bg-sage text-ink" : ""}`} href="/profile">Hi, {user.name.split(" ")[0]}</Link>}
        {!loading && !user && <Link onClick={close} className={`focus-ring rounded-full px-4 py-2 transition hover:bg-sage/70 ${path === "/signin" || path === "/signup" ? "bg-sage text-ink" : ""}`} href="/signin">Sign in</Link>}
        {!loading && user && <button onClick={async () => { await (await import("../lib/api")).logout(); setUser(null); close(); }} className="focus-ring rounded-full px-4 py-2 text-left transition hover:bg-sage/70">Sign out</button>}
        <Link onClick={close} className="focus-ring rounded-full bg-forest px-5 py-2.5 text-ivory shadow-sm transition hover:-translate-y-0.5 hover:bg-ink" href="/analyze">Analyze skin</Link>
      </nav>
    </div>
  </header>;
}
