"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "../../lib/api";
import { useAuth } from "../../components/AuthProvider";

export default function SignUp() {
  const router = useRouter();
  const { setUser } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (name.trim().length < 2) return setError("Enter your name.");
    if (!/^\S+@\S+\.\S+$/.test(email)) return setError("Enter a valid email address.");
    if (password.length < 8) return setError("Use at least 8 characters.");
    if (password !== confirm) return setError("Passwords do not match.");
    if (!consent) return setError("Please acknowledge the privacy notice.");
    setLoading(true);
    try {
      const user = await register({ name, email, password });
      setUser(user);
      router.push("/profile");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Account creation failed.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="mx-auto max-w-lg px-5 pb-24 pt-20"><div className="glass-panel rounded-[32px] p-8 sm:p-10"><div className="text-sm font-semibold uppercase tracking-[.18em] text-forest">AERM account</div><h1 className="mt-4 font-serif text-5xl">Make space for care.</h1><p className="mt-4 text-sm leading-6 text-ink/60">Create a local development account. Your password is hashed by the backend and never stored in the browser.</p><form onSubmit={submit} className="mt-8 space-y-4"><label className="block text-sm font-medium">Name<input required type="text" value={name} onChange={(e) => setName(e.target.value)} className="focus-ring mt-2 block w-full rounded-xl border border-ink/10 bg-ivory px-3 py-3" /></label><label className="block text-sm font-medium">Email<input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="focus-ring mt-2 block w-full rounded-xl border border-ink/10 bg-ivory px-3 py-3" /></label><label className="block text-sm font-medium">Password<input required type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="focus-ring mt-2 block w-full rounded-xl border border-ink/10 bg-ivory px-3 py-3" /></label><p className="text-xs text-ink/50">Use at least 8 characters. Never reuse a password you use elsewhere.</p><label className="block text-sm font-medium">Confirm password<input required type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="focus-ring mt-2 block w-full rounded-xl border border-ink/10 bg-ivory px-3 py-3" /></label><label className="flex items-start gap-3 text-xs leading-5 text-ink/60"><input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-1 h-4 w-4 accent-forest" />I acknowledge the privacy notice and understand this local account is for the academic demo.</label>{error && <p role="alert" className="rounded-xl bg-clay/10 p-3 text-sm text-clay">{error}</p>}<button disabled={loading} className="focus-ring w-full rounded-full bg-forest px-5 py-3 font-semibold text-ivory disabled:opacity-60">{loading ? "Creating account…" : "Create account"}</button></form><p className="mt-6 text-xs leading-5 text-ink/50">Use HTTPS, a managed database, a strong session secret, and an email provider before production deployment.</p><p className="mt-6 text-sm text-ink/60">Already registered? <Link href="/signin" className="font-semibold text-forest underline">Sign in</Link></p></div></main>;
}
