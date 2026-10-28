import Link from "next/link";
import { ArrowDown, ArrowRight, Check, ScanFace, Sparkles } from "lucide-react";
export default function Home() {
  return <main className="grain">
    <section className="mx-auto grid min-h-[calc(100vh-73px)] max-w-7xl items-center gap-14 px-5 pb-20 pt-16 lg:grid-cols-[1.02fr_.98fr] lg:px-8">
      <div className="relative z-10">
        <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-forest/20 bg-white/55 px-4 py-2 text-xs font-semibold uppercase tracking-[.18em] text-forest"><Sparkles size={14} /> multi-view skin intelligence</div>
        <h1 className="max-w-3xl font-serif text-6xl font-normal leading-[.94] tracking-[-.06em] text-ink sm:text-8xl">Understand your skin.<br /><em className="text-clay">Personalize</em> your routine.</h1>
        <p className="mt-8 max-w-xl text-lg leading-8 text-ink/65">A calm, ingredient-aware starting point for your skincare rhythm. Share three facial views and receive a clearly labelled simulated first read.</p>
        <div className="mt-9 flex flex-wrap items-center gap-4"><Link href="/analyze" className="focus-ring inline-flex items-center gap-2 rounded-full bg-forest px-7 py-4 font-semibold text-ivory shadow-soft transition hover:-translate-y-1 hover:bg-ink">Analyze my skin <ArrowRight size={17} /></Link><a href="#how-it-works" className="focus-ring inline-flex items-center gap-2 rounded-full border border-forest/20 px-6 py-4 font-semibold text-forest transition hover:bg-white/60">Explore how it works <ArrowDown size={16} /></a></div>
        <div className="mt-12 grid max-w-lg grid-cols-3 gap-4 border-t border-ink/10 pt-6 text-sm"><div><div className="font-semibold">3 views</div><div className="mt-1 text-ink/50">front, left, right</div></div><div><div className="font-semibold">In memory</div><div className="mt-1 text-ink/50">no photo storage</div></div><div><div className="font-semibold">Demo mode</div><div className="mt-1 text-ink/50">clearly labelled</div></div></div>
      </div>
      <div className="relative mx-auto w-full max-w-[540px]">
        <div className="absolute -inset-8 rounded-[48px] bg-sage/60 blur-3xl" />
        <div className="relative overflow-hidden rounded-[42px] border border-white/80 bg-forest p-5 text-ivory shadow-[0_35px_90px_rgba(24,53,42,.22)]">
          <div className="analysis-orb absolute right-[-8%] top-[-7%] h-56 w-56 rounded-full border border-white/20" />
          <div className="analysis-orb analysis-orb-delay absolute bottom-[18%] left-[-10%] h-28 w-28 rounded-full border border-[#d6bb7c]/40" />
          <div className="relative flex items-center justify-between"><div className="text-xs uppercase tracking-[.22em] text-ivory/60">AERM / skin intelligence</div><ScanFace size={22} className="text-[#d6bb7c]" /></div>
          <div className="relative mt-20"><div className="text-xs uppercase tracking-[.18em] text-[#a6c594]">simulated first read</div><div className="mt-4 font-serif text-5xl leading-[.98]">Notice more.<br /><span className="text-[#a6c594]">Worry less.</span></div><p className="mt-5 max-w-sm text-sm leading-6 text-ivory/65">A thoughtful interface for small, consistent skincare decisions.</p></div>
          <div className="relative mt-20 grid grid-cols-2 gap-3"><div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur"><Check size={18} className="text-[#a6c594]" /><div className="mt-5 text-sm">Evidence-first</div></div><div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur"><Check size={18} className="text-[#a6c594]" /><div className="mt-5 text-sm">Kindly practical</div></div></div>
        </div>
      </div>
    </section>
    <section id="how-it-works" className="mx-auto max-w-7xl scroll-mt-24 px-5 pb-24 lg:px-8"><div className="glass-panel grid gap-8 rounded-[2rem] p-8 sm:grid-cols-3 sm:p-10">{[["01","Share three views","Front, left, and right images give the simulated first check enough context."],["02","Read the signals","See a clearly labelled simulation, confidence, and what to observe next."],["03","Make a small plan","Ingredient-aware matches keep your next routine step simple."]].map(([n,title,copy]) => <div key={n} className="depth-card rounded-2xl p-4"><div className="font-serif text-4xl text-clay">{n}</div><h2 className="mt-4 font-semibold text-forest">{title}</h2><p className="mt-2 text-sm leading-6 text-ink/60">{copy}</p></div>)}</div></section>
  </main>;
}
