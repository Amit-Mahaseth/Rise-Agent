import type { FunnelMetrics } from "../../types/dashboard";

type FunnelViewProps = {
  funnel: FunnelMetrics;
};

const labels = [
  { key: "hot", label: "Hot", className: "hot" },
  { key: "warm", label: "Warm", className: "warm" },
  { key: "cold", label: "Cold", className: "cold" },
] as const;

export function FunnelView({ funnel }: FunnelViewProps) {
  const total = funnel.total_leads || 1;

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Funnel View</h2>
        <span>{funnel.hot_rate}% hot-lead rate</span>
      </div>
      <div className="funnel-stack">
        {labels.map(({ key, label, className }) => {
          const value = funnel[key];
          const width = Math.max((value / total) * 100, value > 0 ? 14 : 0);

          return (
            <div key={key} className="funnel-row">
              <div className="funnel-meta">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
              <div className="funnel-bar-wrap">
                <div className={`funnel-bar funnel-bar--${className}`} style={{ width: `${width}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

