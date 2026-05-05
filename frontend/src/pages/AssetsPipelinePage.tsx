import { useMemo, useState } from "react";
import { NavLink } from "react-router-dom";

import { ConsoleFrame } from "../components/layout/ConsoleFrame";
import { AppShell } from "../components/layout/AppShell";
import { useDashboardData } from "../hooks/useDashboardData";
import type { CallSummaryItem } from "../types/dashboard";

function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function leadScoreTone(c: CallSummaryItem) {
  const cls = (c.classification || "").toUpperCase();
  if (cls === "HOT") {
    return { label: "High", pct: "86" };
  }
  if (cls === "WARM") {
    return { label: "Medium", pct: "58" };
  }
  return { label: "Low", pct: "34" };
}

function MiniEngagementTrend({ seed }: { seed: string }) {
  const pts = useMemo(() => {
    let h = 0;
    for (let i = 0; i < seed.length; i += 1) {
      h = (h + seed.charCodeAt(i) * (i + 1)) % 997;
    }
    const out: string[] = [];
    for (let i = 0; i < 12; i += 1) {
      const y = 18 + ((h * (i + 3)) % 22);
      out.push(`${8 + i * 7},${y}`);
      h = (h * 31 + 17) % 991;
    }
    return out.join(" ");
  }, [seed]);

  return (
    <svg className="mini-trend" viewBox="0 0 88 44" role="img" aria-label="Engagement trend (illustrative)">
      <defs>
        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.25" />
          <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline
        fill="none"
        stroke="var(--primary)"
        strokeWidth="2"
        strokeLinejoin="round"
        strokeLinecap="round"
        points={pts}
      />
    </svg>
  );
}

export function AssetsPipelinePage() {
  const { data, offlineMode } = useDashboardData();
  const leads = data.call_summaries;
  const [selectedId, setSelectedId] = useState("");
  const resolvedId =
    selectedId && leads.some((l) => l.call_id === selectedId)
      ? selectedId
      : (leads[0]?.call_id ?? "");
  const selected = leads.find((l) => l.call_id === resolvedId);
  const totalPipeline = data.funnel.total_leads;

  return (
    <AppShell offlineMode={offlineMode} showMarketingHero={false}>
      <ConsoleFrame>
        <div className="workspace workspace--split">
          <header className="workspace__header">
            <div className="workspace__brand-row">
              <span className="workspace__pill workspace__pill--blue">Desk</span>
              <button type="button" className="workspace__ghost-select">
                North voice desk
              </button>
              <strong className="workspace__balance">
                <span className="workspace__balance-muted">Active leads</span> {totalPipeline.toLocaleString()}
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

          <div className="workspace-split">
            <section className="workspace-panel workspace-panel--list">
              <div className="lead-table__head">
                <span className="lead-table__hc">Borrower</span>
                <span className="lead-table__hc">Class</span>
                <span className="lead-table__hc">Lang</span>
                <span className="lead-table__hc lead-table__hc--tar">Dur</span>
              </div>
              <div className="lead-table__body">
                {leads.map((row) => {
                  const tone = row.classification?.toLowerCase() || "cold";
                  return (
                    <button
                      type="button"
                      key={row.call_id}
                      className={`lead-row ${row.call_id === resolvedId ? "lead-row--active" : ""}`}
                      onClick={() => setSelectedId(row.call_id)}
                    >
                      <span className="lead-row__asset">
                        <span className="lead-row__icon" aria-hidden>
                          {row.customer_name.slice(0, 1)}
                        </span>
                        <span>
                          <span className="lead-row__name">{row.customer_name}</span>
                          <span className="lead-row__sid">{row.lead_id}</span>
                        </span>
                      </span>
                      <span className={`lead-row__pill lead-row__pill--${tone}`}>{row.classification}</span>
                      <span className="lead-row__muted">{row.language}</span>
                      <span className="lead-row__tar muted">{formatDuration(row.duration_seconds)}</span>
                    </button>
                  );
                })}
              </div>
            </section>

            {selected ? (
              <aside className="workspace-panel workspace-panel--detail">
                <div className="detail-head">
                  <div>
                    <h2 className="detail-title">{selected.customer_name}</h2>
                    <p className="detail-sub">{selected.lead_id}</p>
                  </div>
                  <span className={`classification-pill classification-pill--${(selected.classification || "cold").toLowerCase()}`}>
                    {selected.classification}
                  </span>
                </div>

                <div className="detail-actions">
                  <button type="button" className="btn btn--primary btn--block">
                    Hand off to RM
                  </button>
                  <button type="button" className="btn btn--secondary btn--block">
                    Queue recall
                  </button>
                  <button type="button" className="btn btn--secondary btn--block">
                    WhatsApp follow-up
                  </button>
                </div>

                <div className="detail-chart">
                  <div className="detail-chart__head">
                    <span>Engagement</span>
                    <div className="detail-chart__filters">
                      <button type="button" className="is-active">
                        Call
                      </button>
                      <button type="button" disabled>
                        7D
                      </button>
                      <button type="button" disabled>
                        30D
                      </button>
                    </div>
                  </div>
                  <MiniEngagementTrend seed={selected.call_id} />
                  <p className="detail-chart__meta">
                    Model signal: <strong>{leadScoreTone(selected).label}</strong> · coverage{" "}
                    {leadScoreTone(selected).pct}%
                  </p>
                </div>

                <p className="detail-copy">{selected.summary}</p>
                <dl className="detail-kv">
                  <div>
                    <dt>Intent</dt>
                    <dd>{selected.intent}</dd>
                  </div>
                  <div>
                    <dt>Next action</dt>
                    <dd>{selected.next_action?.replace(/_/g, " ")}</dd>
                  </div>
                </dl>
              </aside>
            ) : null}
          </div>
        </div>
      </ConsoleFrame>
    </AppShell>
  );
}
