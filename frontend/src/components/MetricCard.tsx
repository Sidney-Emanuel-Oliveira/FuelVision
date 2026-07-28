interface MetricCardProps {
  label: string;
  value: string;
  detail: string;
  accent: "mint" | "amber" | "coral";
}

export function MetricCard({ label, value, detail, accent }: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${accent}`}>
      <p className="metric-card__label">{label}</p>
      <strong className="metric-card__value">{value}</strong>
      <p className="metric-card__detail">{detail}</p>
    </article>
  );
}
