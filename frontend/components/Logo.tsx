export function Logo({ compact = false }: { compact?: boolean }) {
  return <div className="flex items-center gap-3 text-ink"><img src="/logo.svg" alt="" className="h-10 w-10 rounded-[14px]" />{!compact && <div><div className="text-[17px] font-semibold tracking-[.18em]">AERM</div><div className="-mt-1 text-[9px] uppercase tracking-[.28em] text-forest/70">skin intelligence</div></div>}</div>;
}
