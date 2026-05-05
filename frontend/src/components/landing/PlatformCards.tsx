export function PlatformCards() {
  return (
    <section className="landing-section landing-section--platform" id="platform">
      <div className="landing-platform__intro">
        <h2 className="landing-section__h2 landing-section__h2--center">
          A platform built to elevate every borrower touchpoint
        </h2>
        <p className="landing-section__sub landing-section__sub--center">
          Orchestration, fidelity, and voice quality—production defaults that operations teams can trust.
        </p>
      </div>
      <div className="info-card-grid">
        <article className="info-card">
          <h3 className="info-card__title">Deterministic orchestration</h3>
          <p className="info-card__desc">Graph-based flows with guardrails, branching, and CRM handoffs.</p>
          <div className="info-card__art info-card__art--flow" aria-hidden>
            <div className="flow-node">Start</div>
            <span className="flow-edge" />
            <div className="flow-node flow-node--mid">FAQ+RAG</div>
            <span className="flow-edge" />
            <div className="flow-node">RM</div>
          </div>
        </article>
        <article className="info-card">
          <h3 className="info-card__title">Conversation-grade transcription</h3>
          <p className="info-card__desc">Diarized turns with script alignment for QA and dispute resolution.</p>
          <div className="info-card__art info-card__art--wave" aria-hidden>
            {[12, 28, 18, 40, 22, 35, 16, 44, 20, 38, 14, 32].map((h, i) => (
              <span key={i} className="wave-bar" style={{ height: `${h}%` }} />
            ))}
          </div>
        </article>
        <article className="info-card">
          <h3 className="info-card__title">Multilingual empathetic voice</h3>
          <p className="info-card__desc">Natural prosody with live language detection and code-switching.</p>
          <div className="info-card__art info-card__art--avatar" aria-hidden>
            <div className="avatar-ring" />
            <div className="avatar-glyph">RM</div>
            <span className="avatar-wave" />
          </div>
        </article>
      </div>
    </section>
  );
}
