import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { useDashboardStats, useSeedDemo } from '../hooks/useLeads';
import { Link } from 'react-router-dom';

const CHART_COLORS = { operations: '#141416', transfer: '#EBF981' };

export default function Dashboard() {
  const { data, isLoading, error } = useDashboardStats();
  const seedMutation = useSeedDemo();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-[#141416] border-t-transparent rounded-full" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="bg-white rounded-[2rem] p-8 text-center shadow-soft">
        <p className="text-red-500 mb-2 font-medium">Failed to load dashboard</p>
        <p className="text-gray-400 text-sm">{error.message}</p>
      </div>
    );
  }

  const { stats, funnel, distribution, provider_usage, recent_calls } = data || {};

  // Build funnel data for chart
  const funnelData = funnel ? [
    { stage: 'Contacted', value: funnel.contacted },
    { stage: 'Engaged', value: funnel.engaged },
    { stage: 'Qualified', value: funnel.qualified },
    { stage: 'RM Handoff', value: funnel.rm_handed_off },
  ] : [];

  // Build provider data
  const providerData = provider_usage
    ? Object.entries(provider_usage).filter(([k]) => k !== 'unknown').map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1), value,
      }))
    : [];

  const totalLeads = stats?.total_leads || 0;
  const maxLeads = Math.max(totalLeads, 100);
  const contactedPct = totalLeads > 0 ? Math.round((stats?.contacted / totalLeads) * 100) : 0;
  const conversionPct = stats?.conversion_pct || 0;

  // Pill progress helper
  const renderPills = (filled, total, darkBg) => {
    const pills = [];
    for (let i = 0; i < total; i++) {
      pills.push(
        <div
          key={i}
          className={`flex-1 h-7 rounded-full ${
            i < filled
              ? darkBg ? 'bg-[#141416]' : 'bg-[#141416]'
              : darkBg ? 'bg-[#141416]/20 border border-[#141416]/30 border-dashed' : 'bg-gray-100 border border-gray-200 border-dashed'
          }`}
        />
      );
    }
    return <div className="flex gap-1">{pills}</div>;
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <header className="flex justify-between items-start pt-1 px-1">
        <div className="max-w-2xl">
          <h1 className="text-4xl lg:text-5xl font-medium text-[#141416] leading-tight tracking-tight flex flex-wrap items-center gap-x-3 gap-y-2">
            Managing
            <span className="inline-flex items-center justify-center w-9 h-9 rounded-full border border-gray-200 bg-white">
              <svg fill="none" height="18" width="18" stroke="#141416" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                <path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </span>
            Your Leads
            <br />
            and
            <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-[#EBF981] text-[#141416] transform rotate-12">
              <svg fill="none" height="20" width="20" stroke="#141416" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" viewBox="0 0 24 24">
                <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
              </svg>
            </span>
            Conversions
          </h1>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <button
            className="bg-[#141416] text-white px-5 py-2.5 rounded-full flex items-center gap-2 font-medium text-sm hover:bg-gray-800 transition"
            disabled={seedMutation.isPending}
            onClick={() => seedMutation.mutate()}
          >
            <svg fill="none" height="16" width="16" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M5 12h14"/><path d="M12 5v14"/>
            </svg>
            {seedMutation.isPending ? 'Seeding…' : 'Seed Demo'}
          </button>
        </div>
      </header>

      {seedMutation.isSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl px-4 py-3 text-emerald-700 text-sm">
          ✅ Demo leads seeded! Results will appear in ~30 seconds.
        </div>
      )}

      {/* Navigation Pills */}
      <nav className="flex gap-2 overflow-x-auto pb-1 px-1">
        {[
          { label: 'Overview', to: '/dashboard', end: true },
          { label: 'Leads', to: '/dashboard/leads' },
          { label: 'Calls', to: '/dashboard/calls' },
          { label: 'RM Queue', to: '/dashboard/rm-queue' },
        ].map(({ label, to, end }) => (
          <Link
            key={to}
            to={to}
            className="px-5 py-2 bg-[#141416] text-white rounded-full text-sm font-medium whitespace-nowrap first:bg-[#141416] first:text-white [&:not(:first-child)]:bg-white [&:not(:first-child)]:text-gray-600 hover:bg-gray-100 transition"
          >
            {label}
          </Link>
        ))}
      </nav>

      {/* Top Row Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 px-1">
        {/* Total Leads Card */}
        <div className="bg-white rounded-[2rem] p-6 flex flex-col shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-2 text-[#141416] font-medium text-sm">
              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                <svg fill="none" height="14" width="14" stroke="#141416" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                </svg>
              </div>
              Total Leads
            </div>
          </div>
          <div className="flex items-end gap-3 mb-6">
            <span className="text-5xl font-medium tracking-tight text-[#141416]">{totalLeads}</span>
            <div className="flex flex-col pb-1">
              <div className="flex items-center gap-1 bg-[#EBF981]/30 text-[#141416] text-xs font-semibold px-2 py-0.5 rounded-full mb-1 w-fit">
                {contactedPct}%
              </div>
              <span className="text-gray-400 text-sm">contacted</span>
            </div>
          </div>
          {renderPills(Math.min(Math.ceil((totalLeads / maxLeads) * 7), 7), 7, false)}
        </div>

        {/* Conversion Rate Card */}
        <div className="bg-[#EBF981] rounded-[2rem] p-6 flex flex-col shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-2 text-[#141416] font-medium text-sm">
              <div className="w-8 h-8 rounded-full bg-white/50 flex items-center justify-center">
                <svg fill="none" height="14" width="14" stroke="#141416" strokeWidth="2" viewBox="0 0 24 24">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </div>
              Conversion Rate
            </div>
          </div>
          <div className="flex items-end gap-3 mb-6">
            <span className="text-5xl font-medium tracking-tight text-[#141416]">{conversionPct}%</span>
            <div className="flex flex-col pb-1">
              <div className="flex items-center gap-1 bg-white text-[#141416] text-xs font-semibold px-2 py-0.5 rounded-full mb-1 w-fit">
                {stats?.hot || 0} hot
              </div>
              <span className="text-[#141416]/60 text-sm">/ {totalLeads} total</span>
            </div>
          </div>
          {renderPills(Math.min(Math.ceil(conversionPct / 15), 7), 7, true)}
        </div>

        {/* Promo Card */}
        <div className="bg-[#1D1E22] rounded-[2rem] p-6 flex flex-col justify-between shadow-[0_4px_20px_rgba(0,0,0,0.05)] relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#1D1E22] via-[#1D1E22]/90 to-[#2a2d35] z-0" />
          <div className="relative z-10">
            <h3 className="text-white text-2xl font-medium leading-tight mb-1 flex items-center gap-2">
              Take AI
              <svg fill="none" height="18" width="18" stroke="#EBF981" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M7 17L17 7"/><path d="M7 7h10v10"/>
              </svg>
            </h3>
            <h3 className="text-white text-2xl font-medium leading-tight">
              Voice Agents<br/>to the Next<br/>Level
            </h3>
          </div>
          <Link
            to="/dashboard/leads"
            className="w-full bg-white text-[#141416] py-3 rounded-full font-medium flex justify-center items-center gap-2 relative z-10 hover:bg-gray-100 transition mt-4 text-sm"
          >
            View All Leads
            <svg fill="none" height="14" width="14" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
            </svg>
          </Link>
        </div>
      </div>

      {/* Main Grid */}
      <div className="flex gap-4 px-1">
        {/* Left: Chart */}
        <div className="flex-1 bg-white rounded-[2rem] p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)] flex flex-col min-h-[340px]">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-[#141416] text-lg font-medium">
                <div className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center">
                  <svg fill="none" height="18" width="18" stroke="#141416" strokeWidth="2" viewBox="0 0 24 24">
                    <line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/>
                  </svg>
                </div>
                Statistics
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#141416]" /> Funnel
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#EBF981]" /> Provider
                </div>
              </div>
            </div>
            <span className="px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-xs font-medium text-gray-600">
              2025
            </span>
          </div>
          {/* Funnel Chart */}
          {funnelData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={funnelData} margin={{ left: 0, right: 10 }}>
                <XAxis dataKey="stage" tick={{ fill: '#8A8C8E', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#8A8C8E', fontSize: 11 }} axisLine={false} tickLine={false} width={35} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '16px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
                  labelStyle={{ color: '#141416', fontWeight: 600 }}
                  cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                />
                <Bar dataKey="value" radius={[20, 20, 20, 20]} barSize={32}>
                  {funnelData.map((_, i) => (
                    <Cell key={i} fill={i % 2 === 0 ? '#141416' : '#EBF981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
              No funnel data yet. Seed demo leads to see statistics.
            </div>
          )}
        </div>

        {/* Right column cards */}
        <div className="w-64 flex flex-col gap-3 shrink-0">
          {/* Quick Actions */}
          <div className="grid grid-cols-2 gap-3">
            <Link to="/dashboard/calls" className="bg-white rounded-2xl p-5 flex flex-col items-center justify-center gap-3 shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:shadow-md transition cursor-pointer">
              <div className="w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#141416]">
                <svg fill="none" height="18" width="18" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <span className="font-medium text-[#141416] text-xs">Calls</span>
            </Link>
            <Link to="/dashboard/rm-queue" className="bg-white rounded-2xl p-5 flex flex-col items-center justify-center gap-3 shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:shadow-md transition cursor-pointer">
              <div className="w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center text-[#141416]">
                <svg fill="none" height="18" width="18" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
                </svg>
              </div>
              <span className="font-medium text-[#141416] text-xs">RM Queue</span>
            </Link>
          </div>

          {/* Distribution cards */}
          {[
            { label: 'Hot Leads', val: stats?.hot, color: 'bg-red-50 border-red-100', textColor: 'text-red-600', icon: '🔥' },
            { label: 'Warm Leads', val: stats?.warm, color: 'bg-amber-50 border-amber-100', textColor: 'text-amber-600', icon: '🌤' },
            { label: 'Cold Leads', val: stats?.cold, color: 'bg-blue-50 border-blue-100', textColor: 'text-blue-600', icon: '❄️' },
          ].map(({ label, val, color, textColor, icon }) => (
            <div key={label} className={`bg-white rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.05)] flex items-center gap-3 hover:shadow-md transition`}>
              <div className={`w-10 h-10 rounded-xl ${color} border flex items-center justify-center text-lg`}>
                {icon}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-[#141416] text-sm">{label}</h4>
                <p className={`text-xl font-bold ${textColor}`}>{val ?? 0}</p>
              </div>
              <svg fill="none" height="16" width="16" stroke="#9ca3af" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M7 17L17 7"/><path d="M7 7h10v10"/>
              </svg>
            </div>
          ))}

          {/* LLM Provider */}
          {providerData.length > 0 && (
            <div className="bg-white rounded-2xl p-4 shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
              <h4 className="font-medium text-[#141416] text-sm mb-3">LLM Providers</h4>
              {providerData.map(({ name, value }) => (
                <div key={name} className="flex items-center justify-between text-xs mb-2 last:mb-0">
                  <span className="text-gray-500">{name}</span>
                  <span className="font-semibold text-[#141416] bg-gray-100 px-2 py-0.5 rounded-full">{value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Calls Table */}
      {recent_calls && recent_calls.length > 0 && (
        <div className="bg-white rounded-[2rem] p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)] mx-1">
          <h3 className="text-lg font-medium text-[#141416] mb-4 flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center">
              <svg fill="none" height="16" width="16" stroke="#141416" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3"/>
              </svg>
            </div>
            Recent Calls
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-400 uppercase tracking-wider border-b border-gray-100">
                  <th className="text-left py-3 px-3">Lead</th>
                  <th className="text-left py-3 px-3">Phone</th>
                  <th className="text-left py-3 px-3">Language</th>
                  <th className="text-left py-3 px-3">Duration</th>
                  <th className="text-left py-3 px-3">Status</th>
                  <th className="text-left py-3 px-3">Score</th>
                </tr>
              </thead>
              <tbody>
                {recent_calls.map((call) => (
                  <tr key={call.call_id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-[#141416] flex items-center justify-center text-xs font-bold text-white">
                          {call.lead_name?.charAt(0)}
                        </div>
                        <span className="font-medium text-[#141416]">{call.lead_name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-gray-500">{call.phone}</td>
                    <td className="py-3 px-3 text-gray-500">{call.language}</td>
                    <td className="py-3 px-3 text-gray-500">{call.duration}s</td>
                    <td className="py-3 px-3">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        call.status === 'completed' ? 'bg-emerald-50 text-emerald-600 border border-emerald-200' :
                        call.status === 'in_progress' ? 'bg-amber-50 text-amber-600 border border-amber-200' :
                        'bg-gray-50 text-gray-500 border border-gray-200'
                      }`}>{call.status}</span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${
                        call.classification === 'hot' ? 'bg-red-50 text-red-600' :
                        call.classification === 'warm' ? 'bg-amber-50 text-amber-600' :
                        call.classification === 'cold' ? 'bg-blue-50 text-blue-600' :
                        'bg-gray-50 text-gray-500'
                      }`}>
                        {call.classification === 'hot' ? '🔥' : call.classification === 'warm' ? '🌤' : call.classification === 'cold' ? '❄️' : '⏳'} {call.score ?? '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
