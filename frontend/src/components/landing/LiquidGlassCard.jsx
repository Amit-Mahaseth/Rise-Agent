export default function LiquidGlassCard() {
  return (
    <div className="relative w-[200px] h-[200px] translate-y-[-50px] animate-float">
      {/* Glass card */}
      <div className="liquid-glass-card relative w-full h-full rounded-2xl p-5 flex flex-col justify-between overflow-hidden">
        {/* Border frame pseudo-element done via CSS */}
        <div className="liquid-glass-border absolute inset-0 rounded-2xl pointer-events-none" />

        {/* Content */}
        <div className="relative z-10">
          <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium tracking-wider text-white/60 border border-white/10 bg-white/5">
            [  LIVE DEMO  ]
          </span>
        </div>

        <div className="relative z-10">
          <h3 className="text-[18px] font-semibold leading-tight text-white/90">
            Built for{' '}
            <span className="font-serif italic text-rise-green">Rupeezy</span>{' '}
             Application
          </h3>
        </div>

        <div className="relative z-10">
          <p className="text-[11px] leading-relaxed text-white/40">
            Converts leads in 5 minutes
across 7 Indian languages
          </p>
        </div>
      </div>
    </div>
  );
}
