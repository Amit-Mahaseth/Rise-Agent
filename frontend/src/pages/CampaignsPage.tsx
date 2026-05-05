import { useState } from "react";
import { NavLink } from "react-router-dom";

import { ConsoleFrame } from "../components/layout/ConsoleFrame";
import { AppShell } from "../components/layout/AppShell";
import { VOICE_CAMPAIGNS, type VoiceCampaign } from "../data/campaigns";
import { useDashboardData } from "../hooks/useDashboardData";

export function CampaignsPage() {
  const { offlineMode } = useDashboardData();
  const [active, setActive] = useState<VoiceCampaign>(VOICE_CAMPAIGNS[0]);

  return (
    <AppShell offlineMode={offlineMode} showMarketingHero={false}>
      <ConsoleFrame>
        <div className="workspace">
          <header className="workspace__header">
            <div className="workspace__brand-row">
              <span className="workspace__pill workspace__pill--amber">Voice</span>
              <strong className="workspace__balance">
                <span className="workspace__balance-muted">Campaigns</span> {VOICE_CAMPAIGNS.length} live
              </strong>
            </div>
            <nav className="workspace-tabs" aria-label="Section">
              <NavLink
                end
                to="/assets"
                className={({ isActive }) => `workspace-tab${isActive ? " workspace-tab--active" : ""}`}
              >
                Leads
              </NavLink>
              <NavLink
                end
                to="/collectibles"
                className={({ isActive }) => `workspace-tab${isActive ? " workspace-tab--active" : ""}`}
              >
                Campaigns
              </NavLink>
              <NavLink
                to="/activity"
                className={({ isActive }) => `workspace-tab${isActive ? " workspace-tab--active" : ""}`}
              >
                Activity
              </NavLink>
            </nav>
          </header>

          <div className="campaign-layout">
            <section className="campaign-grid" aria-label="Campaign library">
              {VOICE_CAMPAIGNS.map((c) => (
                <button
                  type="button"
                  key={c.id}
                  className={`campaign-card ${c.id === active.id ? "campaign-card--active" : ""}`}
                  onClick={() => setActive(c)}
                >
                  <div className="campaign-card__art" aria-hidden>
                    <span className="campaign-card__glyph">{c.title.slice(0, 1)}</span>
                  </div>
                  <div className="campaign-card__body">
                    <strong>{c.title}</strong>
                    <span>{c.segment}</span>
                    <span className={`campaign-card__status campaign-card__status--${c.status}`}>
                      {c.status === "active" ? "Running" : "Paused"}
                    </span>
                  </div>
                </button>
              ))}
            </section>

            <aside className="campaign-detail">
              <div className="campaign-detail__hero" aria-hidden>
                <div className="campaign-detail__hero-inner">
                  <span>{active.title}</span>
                </div>
              </div>
              <h2 className="campaign-detail__title">{active.title}</h2>
              <p className="campaign-detail__lede">{active.description}</p>
              <a className="campaign-detail__link" href="#">
                Open playbook
              </a>
              <section className="campaign-detail__section">
                <h3>Routing</h3>
                <p>Languages: {active.languages.join(", ")}</p>
              </section>
              <section className="campaign-detail__section">
                <h3>Performance</h3>
                <dl className="campaign-kv">
                  <div>
                    <dt>24h touches</dt>
                    <dd>{active.touches_24h}</dd>
                  </div>
                  <div>
                    <dt>Hot capture</dt>
                    <dd>{active.hot_capture_rate}</dd>
                  </div>
                </dl>
              </section>
            </aside>
          </div>
        </div>
      </ConsoleFrame>
    </AppShell>
  );
}
