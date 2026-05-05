export default function ScoreBadge({ classification, score }) {
  const config = {
    hot:     { badge: 'badge-hot',     glow: 'glow-hot',  label: '🔥 HOT' },
    warm:    { badge: 'badge-warm',    glow: 'glow-warm', label: '🌤 WARM' },
    cold:    { badge: 'badge-cold',    glow: 'glow-cold', label: '❄️ COLD' },
    pending: { badge: 'badge-pending', glow: '',           label: '⏳ PENDING' },
  };
  const c = config[classification] || config.pending;

  return (
    <span className={`${c.badge} ${c.glow}`}>
      {c.label}{score !== undefined && ` · ${score}`}
    </span>
  );
}
