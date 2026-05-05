import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#8b5cf6', '#6366f1', '#a78bfa', '#c084fc'];

export default function FunnelChart({ funnel }) {
  if (!funnel) return null;

  const data = [
    { stage: 'Contacted',     value: funnel.contacted },
    { stage: 'Engaged',       value: funnel.engaged },
    { stage: 'Qualified',     value: funnel.qualified },
    { stage: 'RM Handed Off', value: funnel.rm_handed_off },
  ];

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
        Conversion Funnel
      </h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis type="number" stroke="#6b7280" fontSize={12} />
          <YAxis type="category" dataKey="stage" stroke="#6b7280" fontSize={12} width={100} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '12px' }}
            labelStyle={{ color: '#d1d5db' }}
            itemStyle={{ color: '#a78bfa' }}
          />
          <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={32}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
