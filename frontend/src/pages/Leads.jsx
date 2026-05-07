import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeads, useCreateLead } from '../hooks/useLeads';

const FILTERS = ['all', 'hot', 'warm', 'cold', 'pending'];

export default function Leads() {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const nav = useNavigate();

  const params = {};
  if (filter !== 'all') params.status = filter;
  if (search) params.search = search;

  const { data, isLoading, error } = useLeads(params);
  const createMutation = useCreateLead();

  const handleAddTest = () => {
    const names = ['Amit Patel', 'Neha Gupta', 'Ravi Verma', 'Sunita Devi', 'Vikram Singh'];
    const name = names[Math.floor(Math.random() * names.length)];
    const phone = `+9198765${String(Math.floor(Math.random() * 100000)).padStart(5, '0')}`;
    createMutation.mutate({ name, phone, source: 'test', language_hint: 'hi-IN' });
  };

  const badgeClass = (status) => {
    if (status?.includes('hot')) return 'bg-red-50 text-red-600 border-red-200';
    if (status?.includes('warm')) return 'bg-amber-50 text-amber-600 border-amber-200';
    if (status === 'cold') return 'bg-blue-50 text-blue-600 border-blue-200';
    return 'bg-gray-50 text-gray-500 border-gray-200';
  };

  return (
    <div className="space-y-5 px-1 pt-2">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-medium text-[#141416]">Leads</h1>
        <button
          className="bg-[#141416] text-white px-5 py-2.5 rounded-full flex items-center gap-2 font-medium text-sm hover:bg-gray-800 transition"
          onClick={handleAddTest}
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? 'Adding…' : '+ Add Test Lead'}
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-2">
          {FILTERS.map((f) => (
            <button
              key={f}
              className={`px-4 py-2 rounded-full text-xs font-medium transition-all ${
                filter === f
                  ? 'bg-[#141416] text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Search by name or phone…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 bg-white border border-gray-200 rounded-full px-5 py-2 text-sm focus:outline-none focus:border-[#141416] transition-colors placeholder:text-gray-400"
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin w-8 h-8 border-2 border-[#141416] border-t-transparent rounded-full" />
        </div>
      ) : error ? (
        <div className="bg-white rounded-[2rem] p-10 text-center shadow-soft text-red-500">Failed to load leads</div>
      ) : !data?.leads?.length ? (
        <div className="bg-white rounded-[2rem] p-16 text-center shadow-soft">
          <p className="text-gray-500 text-lg">No leads found</p>
          <p className="text-gray-400 text-sm mt-2">Add a test lead or seed demo data from the Dashboard</p>
        </div>
      ) : (
        <div className="bg-white rounded-[2rem] overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-400 uppercase tracking-wider border-b border-gray-100 bg-gray-50/50">
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Phone</th>
                  <th className="text-left py-3 px-4">Language</th>
                  <th className="text-left py-3 px-4">Source</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Created</th>
                </tr>
              </thead>
              <tbody>
                {data.leads.map((lead) => (
                  <tr
                    key={lead.id}
                    className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors cursor-pointer"
                    onClick={() => nav(`/dashboard/calls?lead_id=${lead.id}`)}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-[#141416] flex items-center justify-center text-xs font-bold text-white shrink-0">
                          {lead.name?.charAt(0)}
                        </div>
                        <span className="font-medium text-[#141416]">{lead.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-500">{lead.phone}</td>
                    <td className="py-3 px-4 text-gray-500">{lead.language}</td>
                    <td className="py-3 px-4 text-gray-500">{lead.source}</td>
                    <td className="py-3 px-4">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-medium border ${badgeClass(lead.status)}`}>
                        {lead.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs">
                      {lead.created_at ? new Date(lead.created_at).toLocaleDateString() : '—'}
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
