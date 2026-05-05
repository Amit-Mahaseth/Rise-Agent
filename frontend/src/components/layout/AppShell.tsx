import { ReactNode } from "react";
import { NavLink } from "react-router-dom";

type AppShellProps = {
  children: ReactNode;
  offlineMode: boolean;
  /** Full marketing hero — only the home overview uses this. */
  showMarketingHero?: boolean;
};

const primaryNav = [
  { to: "/", label: "Overview", end: true },
  { to: "/assets", label: "Leads" },
  { to: "/collectibles", label: "Campaigns" },
  { to: "/activity", label: "Activity" },
] as const;

export function AppShell({ children, offlineMode, showMarketingHero = false }: AppShellProps) {
  return (
    <div className="page">
      <header className="top-nav">
        <div className="top-nav__inner">
          <NavLink to="/" className="top-nav__logo" end>
            RiseAgent
          </NavLink>
          <nav className="top-nav__links" aria-label="Primary">
            {primaryNav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={"end" in item ? item.end : false}
                className={({ isActive }) => `top-nav__link${isActive ? " top-nav__link--active" : ""}`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="top-nav__actions">
            <span className={`top-nav__status ${offlineMode ? "top-nav__status--warn" : ""}`}>
              {offlineMode ? "Offline mode" : "Live"}
            </span>
            <button type="button" className="btn btn--primary">
              Book a demo
            </button>
          </div>
        </div>
      </header>

      <div className={`app-shell${showMarketingHero ? "" : " app-shell--tight"}`}>
        {showMarketingHero ? (
          <section className="hero hero--marketing">
            <p className="hero__eyebrow">Built for lending. Tuned for trust.</p>
            <h1 className="hero__title">The agentic voice for conversion.</h1>
            <p className="hero__lede">
              Instant outbound calls, multilingual detection, and a single surface for funnel health,
              call intelligence, and RM handoffs—without losing the human touch.
            </p>
            <div className="hero__ctas">
              <button type="button" className="btn btn--primary btn--lg">
                Book a demo
              </button>
              <NavLink to="/assets" className="btn btn--ghost btn--lg">
                View platform
              </NavLink>
            </div>

            <div className="hero-visual" aria-hidden>
              <div className="hero-visual__glow" />
              <div className="hero-visual__card hero-visual__card--main">
                <div className="hero-visual__card-head">
                  <span>Call campaign manager</span>
                  <span className="hero-visual__pill">Active</span>
                </div>
                <div className="hero-visual__bars">
                  <div className="hero-visual__bar" style={{ width: "72%" }} />
                  <div className="hero-visual__bar hero-visual__bar--muted" style={{ width: "48%" }} />
                  <div className="hero-visual__bar hero-visual__bar--accent" style={{ width: "88%" }} />
                </div>
                <div className="hero-visual__mini">
                  <div className="hero-visual__spark" />
                  <span>Hot rate trending up</span>
                </div>
              </div>
              <div className="hero-visual__bubble hero-visual__bubble--1">Listening…</div>
              <div className="hero-visual__bubble hero-visual__bubble--2">Lead qualified</div>
            </div>

            <div className={`hero-banner ${offlineMode ? "hero-banner--warn" : ""}`}>
              <strong>{offlineMode ? "Offline sample data" : "Connected to RiseAgent backend"}</strong>
              <p>
                Tracks Hot/Warm/Cold distribution, recent call intelligence, and RM workload in one
                view.
              </p>
            </div>
          </section>
        ) : null}

        <main className="main-content">{children}</main>
      </div>
    </div>
  );
}
