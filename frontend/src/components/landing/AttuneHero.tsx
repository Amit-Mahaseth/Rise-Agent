export function AttuneHero() {
  return (
    <section className="landing-hero" id="top">
      <p className="landing-hero__eyebrow">Best for lending. Tuned for trust.</p>
      <h1 className="landing-hero__title">The agentic voice for conversion.</h1>
      <p className="landing-hero__lede">
        Outbound calls that stay on-script, listen in 10+ languages, and hand off to your desk with
        context—so every borrower gets a clear next step, every time.
      </p>
      <div className="landing-hero__ctas">
        <button type="button" className="btn btn--primary btn--lg">
          Book a demo
        </button>
      </div>

      <div className="hero-composite" aria-hidden>
        <div className="hero-composite__bg" />
        <div className="hero-composite__glow" />

        <div className="hero-composite__main hero-card-anim">
          <div className="hero-composite__title-row">
            <span className="hero-composite__title">Call campaign manager</span>
            <span className="hero-composite__badge">Active</span>
          </div>
          <p className="hero-composite__label">Campaign progress</p>
          <div className="hero-composite__progress">
            <div className="hero-composite__progress-fill" style={{ width: "68%" }} />
          </div>
          <div className="hero-composite__subgrid">
            <div className="hero-composite__mini">
              <span>Touchpoints</span>
              <strong>1,248</strong>
            </div>
            <div className="hero-composite__mini">
              <span>Hot rate</span>
              <strong>24%</strong>
            </div>
          </div>
        </div>

        <div className="hero-composite__side hero-card-anim hero-composite__side--chart">
          <p className="hero-composite__side-title">Handle time</p>
          <div className="hero-composite__bars">
            {[40, 65, 45, 80, 55, 70, 50].map((h, i) => (
              <div key={i} className="hero-composite__bar" style={{ height: `${h}%` }} />
            ))}
          </div>
        </div>

        <div className="hero-composite__verify hero-card-anim">
          <div className="hero-composite__verify-icon" />
          <div>
            <p className="hero-composite__verify-title">Verify caller ID</p>
            <p className="hero-composite__verify-sub">Device &amp; carrier match</p>
          </div>
          <span className="hero-composite__verify-ok">Verified</span>
        </div>

        <div className="hero-composite__chat">
          <p>Can you confirm the loan amount and preferred callback window?</p>
        </div>
      </div>
    </section>
  );
}
