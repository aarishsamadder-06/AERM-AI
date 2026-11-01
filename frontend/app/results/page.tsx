"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, Info, Sparkles } from "lucide-react";
import type { Analysis } from "../../lib/api";
import { Atmosphere } from "../../components/Atmosphere";

const viewTitles = {
  front: "Front view",
  left: "Left profile",
  right: "Right profile",
} as const;

export default function Results() {
  const [result, setResult] = useState<Analysis | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("aerm-analysis");
    if (!raw) return;
    try {
      setResult(JSON.parse(raw));
    } catch {
      sessionStorage.removeItem("aerm-analysis");
    }
  }, []);

  if (!result) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-24 text-center">
        <Sparkles className="mx-auto text-forest" size={40} />
        <h1 className="mt-5 text-3xl font-semibold">Your analysis is waiting.</h1>
        <Link href="/analyze" className="mt-6 inline-flex rounded-full bg-forest px-5 py-3 text-ivory">
          Start an analysis
        </Link>
      </main>
    );
  }

  const finding = result.finding;
  const quality = result.image_quality;

  return (
    <main className="mx-auto max-w-7xl px-5 pb-24 pt-14 lg:px-8">
      <Atmosphere variant="quiet" />
      <div className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <div className="text-sm font-semibold uppercase tracking-[.16em] text-forest">02 / your skin note</div>
          <h1 className="mt-4 font-serif text-6xl font-normal leading-none tracking-[-.05em]">A gentle first read.</h1>
        </div>
        <div className="rounded-2xl border border-forest/10 bg-sage/80 px-5 py-4 shadow-soft">
          <div className="text-xs uppercase tracking-widest text-forest/70">simulated confidence</div>
          <div className="mt-1 text-3xl font-semibold text-forest">{Math.round(finding.confidence * 100)}%</div>
          <div className="mt-2 h-1.5 w-28 overflow-hidden rounded-full bg-forest/10">
            <div className="h-full rounded-full bg-forest" style={{ width: `${Math.round(finding.confidence * 100)}%` }} />
          </div>
        </div>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-[1.2fr_.8fr]">
        <section className="depth-card relative overflow-hidden rounded-[30px] bg-forest p-8 text-ivory shadow-[0_26px_70px_rgba(24,53,42,.18)]">
          <div className="result-sheen" />
          <div className="relative flex items-center gap-2 text-sm text-ivory/60">
            <CheckCircle2 size={18} className="text-[#A6C594]" /> simulated first analysis
          </div>
          <h2 className="relative mt-8 font-serif text-5xl">{finding.label}</h2>
          <p className="relative mt-5 max-w-xl text-lg leading-8 text-ivory/70">{finding.summary}</p>
          <div className="relative mt-9 inline-flex rounded-full bg-ivory/10 px-4 py-2 text-sm capitalize">
            signal level · {finding.severity}
          </div>
        </section>
        <section className="glass-panel depth-card rounded-[30px] p-8">
          <h2 className="text-xl font-semibold text-forest">Structured read</h2>
          <p className="mt-3 text-sm text-ink/60">
            Views: {result.views.join(" · ")} · Concerns: {result.detected_concerns.join(" · ")}
          </p>
          <p className="mt-3 text-sm text-ink/60">Matched ingredients: {result.matched_ingredients.join(" · ")}</p>
          <ul className="mt-5 space-y-4">
            {result.observations.map((item) => (
              <li key={item} className="flex gap-3 text-sm leading-6 text-ink/70">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-clay" />
                {item}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {quality?.available && (
        <section className="glass-panel depth-card mt-6 rounded-[30px] p-8" aria-labelledby="image-quality-heading">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[.16em] text-forest">
                <Info size={16} aria-hidden="true" /> Capture check
              </div>
              <h2 id="image-quality-heading" className="mt-3 text-2xl font-semibold text-forest">
                Image quality by view
              </h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-ink/60">
                This separate image-gradability check only indicates whether each upload is suitable for the experiment.
                It is not a skin-health score, diagnosis, confidence, or cosmetic finding.
              </p>
            </div>
            <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold text-ink/60">{quality.model}</span>
          </div>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            {quality.views.map((item) => {
              const sufficient = item.label === "quality_sufficient";
              return (
                <div
                  key={item.view}
                  className={`rounded-2xl border p-4 ${
                    sufficient ? "border-forest/20 bg-sage/50" : "border-clay/30 bg-[#fff4ed]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-widest text-ink/50">
                        {viewTitles[item.view]}
                      </div>
                      <div className={`mt-2 flex items-center gap-2 font-semibold ${sufficient ? "text-forest" : "text-clay"}`}>
                        {sufficient ? (
                          <CheckCircle2 size={18} aria-hidden="true" />
                        ) : (
                          <AlertTriangle size={18} aria-hidden="true" />
                        )}
                        {sufficient ? "Quality sufficient" : "Quality insufficient"}
                      </div>
                    </div>
                    <span className={`rounded-full px-2 py-1 text-xs font-semibold ${sufficient ? "bg-forest/10 text-forest" : "bg-clay/10 text-clay"}`}>
                      {sufficient ? "Pass" : "Retry"}
                    </span>
                  </div>
                  {!sufficient && (
                    <p className="mt-3 text-sm leading-6 text-clay">
                      Upload a clearer, well-lit {viewTitles[item.view].toLowerCase()} image if you want to retry this capture.
                    </p>
                  )}
                  <p className="mt-3 text-xs text-ink/45">
                    Raw decision score: {item.decision_score.toFixed(3)} · not a probability
                  </p>
                </div>
              );
            })}
          </div>
          <p className="mt-5 text-xs leading-5 text-ink/45">{quality.notice}</p>
        </section>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="glass-panel depth-card rounded-[30px] p-8">
          <h2 className="text-xl font-semibold text-forest">Routine</h2>
          <div className="mt-5 space-y-3">
            {result.routine.map((step) => (
              <div key={`${step.time}-${step.step}`} className="rounded-2xl bg-mist/80 p-4 transition hover:bg-sage/60">
                <div className="text-xs font-semibold uppercase tracking-widest text-forest">
                  {step.time} · {step.step}
                </div>
                <p className="mt-2 text-sm text-ink/70">{step.action}</p>
                <p className="mt-1 text-xs text-ink/50">{step.rationale}</p>
              </div>
            ))}
          </div>
          <h2 className="mt-7 text-xl font-semibold text-forest">Your next small steps</h2>
          <div className="mt-4 space-y-3">
            {result.recommendations.map((item, index) => (
              <div key={item} className="flex gap-4 rounded-2xl bg-mist/80 p-4">
                <span className="font-serif text-2xl text-forest">0{index + 1}</span>
                <p className="text-sm leading-6 text-ink/70">{item}</p>
              </div>
            ))}
          </div>
        </section>
        <section className="glass-panel depth-card rounded-[30px] p-8">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-forest">Ingredient-aware matches</h2>
            <Link href="/products" className="focus-ring rounded-lg text-sm font-semibold text-forest">
              View all <ArrowRight className="inline" size={15} />
            </Link>
          </div>
          <div className="mt-5 space-y-3">
            {result.products.map((item) => (
              <div key={item.id} className="depth-card rounded-2xl border border-ink/10 p-4">
                <div className="flex justify-between gap-2">
                  <div>
                    <div className="text-xs uppercase tracking-widest text-forest/60">{item.category}</div>
                    <div className="mt-1 font-semibold text-forest">{item.name}</div>
                  </div>
                  <div className="font-semibold">₹{item.price_inr}</div>
                </div>
                <p className="mt-1 text-sm text-ink/60">{item.why}</p>
                <p className="mt-2 text-xs text-ink/45">{item.ingredients.join(" · ")}</p>
              </div>
            ))}
          </div>
          <h2 className="mt-7 text-xl font-semibold text-forest">Why these matches</h2>
          <ul className="mt-3 space-y-2 text-sm text-ink/60">
            {result.rationale.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </section>
      </div>
      <p className="mt-6 text-xs leading-5 text-ink/45">{result.simulation_notice}</p>
    </main>
  );
}
