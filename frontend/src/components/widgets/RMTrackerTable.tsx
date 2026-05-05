import type { RMTrackingItem } from "../../types/dashboard";

type RMTrackerTableProps = {
  rows: RMTrackingItem[];
};

export function RMTrackerTable({ rows }: RMTrackerTableProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>RM Tracking</h2>
        <span>Relationship manager load</span>
      </div>
      <div className="rm-table">
        <div className="rm-row rm-row--head">
          <span>RM</span>
          <span>Assigned</span>
          <span>Hot</span>
          <span>Warm</span>
        </div>
        {rows.map((row) => (
          <div className="rm-row" key={row.rm_name}>
            <span>{row.rm_name}</span>
            <span>{row.assigned_leads}</span>
            <span>{row.hot_leads}</span>
            <span>{row.warm_leads}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

