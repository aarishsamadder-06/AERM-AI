"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../../components/AuthProvider";

export default function Profile() {
  const router = useRouter();
  const { user, loading } = useAuth();
  if (loading) return <main className="mx-auto max-w-2xl px-5 py-24 text-center text-ink/60">Checking your session…</main>;
  if (!user) return <main className="mx-auto max-w-2xl px-5 pb-24 pt-20"><div className="glass-panel rounded-[32px] p-8 sm:p-10"><div className="text-sm font-semibold uppercase tracking-[.18em] text-forest">Profile</div><h1 className="mt-4 font-serif text-5xl">Sign in to continue.</h1><p className="mt-5 leading-7 text-ink/60">Your profile is protected. Sign in to manage your account and keep future saved care plans connected.</p><div className="mt-7 flex gap-3"><Link href="/signin" className="focus-ring rounded-full bg-forest px-5 py-3 font-semibold text-ivory">Sign in</Link><Link href="/signup" className="focus-ring rounded-full border border-forest/20 px-5 py-3 font-semibold text-forest">Create account</Link></div></div></main>;
  return <main className="mx-auto max-w-3xl px-5 pb-24 pt-20"><div className="glass-panel rounded-[32px] p-8 sm:p-10"><div className="text-sm font-semibold uppercase tracking-[.18em] text-forest">Your account</div><h1 className="mt-4 font-serif text-5xl">{user.name}</h1><p className="mt-4 text-ink/60">{user.email}</p><div className="mt-8 grid gap-4 sm:grid-cols-2"><div className="rounded-2xl bg-sage/60 p-5"><div className="text-xs uppercase tracking-widest text-forest/70">Account status</div><p className="mt-2 font-semibold text-forest">Signed in</p><p className="mt-1 text-sm text-ink/60">Your session uses an HTTP-only cookie.</p></div><div className="rounded-2xl bg-mist p-5"><div className="text-xs uppercase tracking-widest text-forest/70">Saved history</div><p className="mt-2 font-semibold text-forest">Coming next</p><p className="mt-1 text-sm text-ink/60">Analysis history is not persisted yet.</p></div></div><button onClick={() => router.push("/routine")} className="focus-ring mt-8 rounded-full bg-forest px-5 py-3 font-semibold text-ivory">Open routine planner</button></div></main>;
}
