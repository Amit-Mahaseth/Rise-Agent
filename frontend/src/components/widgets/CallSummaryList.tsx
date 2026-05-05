import type { CallSummaryItem } from "../../types/dashboard";

type CallSummaryListProps = {
  items: CallSummaryItem[];
};

export function CallSummaryList({ items }: CallSummaryListProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Recent Call Summaries</h2>
        <span>{items.length} records</span>
      </div>
      <div className="summary-list">
        {items.map((item) => (
          <article className="summary-card" key={item.call_id}>
            <div className="summary-header">
              <div>
                <strong>{item.customer_name}</strong>
                <span>{item.lead_id}</span>
              </div>
              <span className={`classification-pill classification-pill--${(item.classification || "cold").toLowerCase()}`}>
                {item.classification || "UNCLASSIFIED"}
              </span>
            </div>
            <p>{item.summary || "No summary yet. The call is likely still in progress."}</p>
            <div className="summary-grid">
              <span>Language: {item.language || "Unknown"}</span>
              <span>Intent: {item.intent || "Pending"}</span>
              <span>Action: {item.next_action || "Pending"}</span>
              <span>Duration: {item.duration_seconds}s</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

