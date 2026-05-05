import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { useDashboardStats, useSeedDemo } from '../hooks/useLeads';
import StatsBar from '../components/StatsBar';
import FunnelChart from '../components/FunnelChart';
import ScoreBadge from '../components/ScoreBadge';

const PIE_COLORS = { hot: '#ef4444', warm: '#facc15', cold: '#60a5fa', pending: '#6b7280' };

export default function Dashboard() {
  const { data, isLoading, error } = useDashboardStats();
  const seedMutation = useSeedDemo();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="card text-center py-10">
        <p className="text-red-400 mb-2">Failed to load dashboard</p>
        <p className="text-gray-500 text-sm">{error.message}</p>
      </div>
    );
  }

  const { stats, funnel, distribution, provider_usage, recent_calls } = data || {};
  const pieData = distribution
    ? Object.entries(distribution).filter(([,v]) => v > 0).map(([name, value]) => ({ name, value }))
    : [];

  const PROVIDER_COLORS = { groq: '#8b5cf6', gemini: '#06b6d4', none: '#6b7280', unknown: '#4b5563' };
  const providerData = provider_usage
    ? Object.entries(provider_usage).filter(([k]) => k !== 'unknown').map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value, fill: PROVIDER_COLORS[name] || '#6b7280' }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-1">Real-time lead conversion analytics</p>
        </div>
        <button
          className="btn-primary text-sm"
          disabled={seedMutation.isPending}
          onClick={() => seedMutation.mutate()}
        >
          {seedMutation.isPending ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
              Running…
            </span>
          ) : '🚀 Seed Demo Leads'}
        </button>
      </div>

      {seedMutation.isSuccess && (
        <div className="card-sm bg-emerald-900/30 border-emerald-700/30 text-emerald-300 text-sm">
          ✅ Demo leads seeded! Simulations are running in the background. Results will appear in ~30 seconds.
        </div>
      )}

      {/* Stats Bar */}
      <StatsBar stats={stats} />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FunnelChart funnel={funnel} />

        <div className="card">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Lead Distribution
          </h3>
          {pieData.length === 0 ? (
            <p className="text-gray-600 text-center py-16">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={4}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={PIE_COLORS[entry.name] || '#6b7280'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '12px' }}
                  labelStyle={{ color: '#d1d5db' }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
          <div className="flex justify-center gap-6 mt-2">
            {pieData.map((entry) => (
              <div key={entry.name} className="flex items-center gap-1.5 text-xs text-gray-400">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: PIE_COLORS[entry.name] }} />
                {entry.name}: {entry.value}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* LLM Provider Usage */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          LLM Provider Usage — Groq vs Gemini
        </h3>
        {providerData.length === 0 ? (
          <p className="text-gray-600 text-center py-8">No LLM usage data yet</p>
        ) : (
          <div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={providerData} layout="vertical" margin={{ left: 10, right: 30 }}>
                <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: '#d1d5db', fontSize: 13, fontWeight: 500 }} axisLine={false} tickLine={false} width={70} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '12px' }}
                  labelStyle={{ color: '#d1d5db' }}
                  formatter={(value) => [`${value} turns`, 'Requests']}
                />
                <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={28}>
                  {providerData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-2">
              {providerData.map((entry) => (
                <div key={entry.name} className="flex items-center gap-1.5 text-xs text-gray-400">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: entry.fill }} />
                  {entry.name}: {entry.value} requests
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Recent Calls
        </h3>
        {!recent_calls || recent_calls.length === 0 ? (
          <p className="text-gray-600 text-center py-8">No calls yet. Seed demo leads to get started!</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
                  <th className="text-left py-3 px-2">Lead</th>
                  <th className="text-left py-3 px-2">Phone</th>
                  <th className="text-left py-3 px-2">Language</th>
                  <th className="text-left py-3 px-2">Duration</th>
                  <th className="text-left py-3 px-2">Status</th>
                  <th className="text-left py-3 px-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {recent_calls.map((call) => (
                  <tr key={call.call_id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                    <td className="py-3 px-2 font-medium">{call.lead_name}</td>
                    <td className="py-3 px-2 text-gray-400">{call.phone}</td>
                    <td className="py-3 px-2 text-gray-400">{call.language}</td>
                    <td className="py-3 px-2 text-gray-400">{call.duration}s</td>
                    <td className="py-3 px-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        call.status === 'completed' ? 'bg-emerald-500/15 text-emerald-400' :
                        call.status === 'in_progress' ? 'bg-yellow-500/15 text-yellow-400' :
                        'bg-gray-500/15 text-gray-400'
                      }`}>{call.status}</span>
                    </td>
                    <td className="py-3 px-2">
                      <ScoreBadge classification={call.classification} score={call.score} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
