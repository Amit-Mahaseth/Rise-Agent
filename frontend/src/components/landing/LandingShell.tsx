import { ReactNode } from "react";
import { NavLink } from "react-router-dom";

function Chevron() {
  return (
    <svg className="landing-nav__chev" width="12" height="12" viewBox="0 0 24 24" aria-hidden>
      <path
        fill="currentColor"
        d="M12 15.5 4.5 8l1.4-1.4L12 12.7l6.1-6.1L19.5 8 12 15.5Z"
      />
    </svg>
  );
}

type LandingShellProps = {
  children: ReactNode;
  offlineMode?: boolean;
};

export function LandingShell({ children, offlineMode }: LandingShellProps) {
  return (
    <div className="landing-page">
      <header className="landing-nav">
        <div className="landing-nav__inner">
          <NavLink to="/" className="landing-nav__logo" end>
            RiseAgent
          </NavLink>
          <nav className="landing-nav__links" aria-label="Marketing">
            <a className="landing-nav__item" href="#platform">
              Platform
              <Chevron />
            </a>
            <a className="landing-nav__item" href="#solutions">
              Solutions
              <Chevron />
            </a>
            <a className="landing-nav__item" href="#company">
              Company
              <Chevron />
            </a>
            <a className="landing-nav__item" href="#resources">
              Resources
              <Chevron />
            </a>
          </nav>
          <div className="landing-nav__actions">
            {offlineMode !== undefined ? (
              <span
                className={`landing-nav__pill ${offlineMode ? "landing-nav__pill--warn" : ""}`}
                title="API status"
              >
                {offlineMode ? "Sample data" : "Live"}
              </span>
            ) : null}
            <NavLink to="/assets" className="landing-nav__console">
              Console
            </NavLink>
            <button type="button" className="btn btn--primary landing-nav__cta">
              Book a demo
            </button>
          </div>
        </div>
      </header>
      {children}
      <footer className="landing-footer">
        <div className="landing-footer__inner">
          <p>© {new Date().getFullYear()} RiseAgent. Voice orchestration for modern lending.</p>
          <NavLink to="/assets" className="landing-footer__link">
            Open operator console →
          </NavLink>
        </div>
      </footer>
    </div>
  );
}
