import { NavLink } from "react-router-dom";
import { useState } from "react";

import { ConsoleFrame } from "../components/layout/ConsoleFrame";
import { AppShell } from "../components/layout/AppShell";
import { useDashboardData } from "../hooks/useDashboardData";

type ActivityStatus = "completed" | "in_progress" | "missed";

function statusFor(item: { duration_seconds: number; classification: string | null }): ActivityStatus {
  if (item.duration_seconds < 60) {
    return "missed";
  }
  if (item.duration_seconds > 180) {
    return "completed";
  }
  return "in_progress";
}

function formatWhen(index: number) {
  const hours = 9 + index * 2;
  return `Today · ${hours.toString().padStart(2, "0")}:42`;
}

export function ActivityPage() {
  const { data, offlineMode, liveTranscript, tuningDebug } = useDashboardData();
  const items = data.call_summaries;
  const [showDebug, setShowDebug] = useState(false);

  return (
    <AppShell offlineMode={offlineMode} showMarketingHero={false}>
      <ConsoleFrame>
        <div className="workspace">
          <header className="workspace__header">
            <div className="workspace__brand-row">
              <span className="workspace__pill">Log</span>
              <strong className="workspace__balance">
                <span className="workspace__balance-muted">Recent voice events</span> {items.length}
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
                end
                to="/activity"
                className={({ isActive }) => `workspace-tab${isActive ? " workspace-tab--active" : ""}`}
              >
                Activity
              </NavLink>
            </nav>
          </header>

          <section className="activity-list" aria-label="Call activity">
            {items.map((row, i) => {
              const st = statusFor(row);
              return (
                <article className="activity-row" key={row.call_id}>
                  <div className={`activity-row__icon activity-row__icon--${st}`} aria-hidden>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
                      <path d="M7 12h10M12 7l5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <div className="activity-row__main">
                    <strong>Inbound voice · {row.customer_name}</strong>
                    <span className="muted">{row.lead_id}</span>
                  </div>
                  <div className="activity-row__meta muted">{formatWhen(i)}</div>
                  <div className="activity-row__amount">
                    <span>{Math.floor(row.duration_seconds / 60)}m {row.duration_seconds % 60}s</span>
                    <span className="muted">{row.language}</span>
                  </div>
                  <span className={`activity-badge activity-badge--${st}`}>
                    {st === "completed" ? "Completed" : st === "in_progress" ? "In progress" : "Short"}
                  </span>
                </article>
              );
            })}
          </section>

          <section className="panel" style={{ marginTop: "16px" }} aria-label="Live call transcript">
            <div className="panel-heading">
              <h2>Live Call View</h2>
              <span>Streaming transcript</span>
            </div>
            {items[0] ? (
              <div className="summary-list">
                {(liveTranscript[items[0].call_id] ?? ["Waiting for live speech..."]).map((line, idx) => (
                  <div key={`${items[0].call_id}-${idx}`} className="summary-card">
                    {line}
                  </div>
                ))}
              </div>
            ) : null}
          </section>

          <section className="panel" style={{ marginTop: "16px" }} aria-label="Tuning debug">
            <div className="panel-heading">
              <h2>Tuning Debug</h2>
              <button
                type="button"
                className="btn btn--secondary"
                onClick={() => setShowDebug((v) => !v)}
                style={{ padding: "6px 10px" }}
              >
                {showDebug ? "Hide" : "Show"}
              </button>
            </div>
            {showDebug ? (
              <div className="summary-list">
                <div className="summary-card">
                  <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                    {JSON.stringify(tuningDebug ?? { status: "waiting_for_debug_events" }, null, 2)}
                  </pre>
                </div>
              </div>
            ) : null}
          </section>
        </div>
      </ConsoleFrame>
    </AppShell>
  );
}
