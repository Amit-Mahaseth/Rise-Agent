type MetricCardProps = {
  label: string;
  value: string;
  accent: "hot" | "warm" | "cold" | "neutral";
};

export function MetricCard({ label, value, accent }: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${accent}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

