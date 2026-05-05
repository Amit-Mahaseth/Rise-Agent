export default function StatsBar({ stats }) {
  if (!stats) return null;
  const items = [
    { label: 'Total Leads',    value: stats.total_leads,    color: 'text-white' },
    { label: 'Contacted',      value: stats.contacted,      color: 'text-violet-400' },
    { label: 'Hot',            value: stats.hot,            color: 'text-red-400' },
    { label: 'Warm',           value: stats.warm,           color: 'text-yellow-300' },
    { label: 'Cold',           value: stats.cold,           color: 'text-blue-400' },
    { label: 'Conversion',     value: `${stats.conversion_pct}%`, color: 'text-emerald-400' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
      {items.map(({ label, value, color }) => (
        <div key={label} className="card-sm text-center group hover:border-gray-600 transition-all duration-300">
          <p className="text-xs uppercase tracking-wider text-gray-500 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${color} group-hover:scale-110 transition-transform duration-300`}>
            {value}
          </p>
        </div>
      ))}
    </div>
  );
}
