import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeads, useCreateLead } from '../hooks/useLeads';
import ScoreBadge from '../components/ScoreBadge';

const FILTERS = ['all', 'hot', 'warm', 'cold', 'pending'];

export default function Leads() {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const nav = useNavigate();

  const statusMap = {
    all: undefined,
    hot: 'hot',
    warm: 'warm',
    cold: 'cold',
    pending: 'pending',
  };
  const params = {};
  if (filter !== 'all') params.status = statusMap[filter];
  if (search) params.search = search;

  const { data, isLoading, error } = useLeads(params);
  const createMutation = useCreateLead();

  const handleAddTest = () => {
    const names = ['Amit Patel', 'Neha Gupta', 'Ravi Verma', 'Sunita Devi', 'Vikram Singh'];
    const name = names[Math.floor(Math.random() * names.length)];
    const phone = `+9198765${String(Math.floor(Math.random() * 100000)).padStart(5, '0')}`;
    createMutation.mutate({ name, phone, source: 'test', language_hint: 'hi-IN' });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            Leads
          </h1>
          <p className="text-sm text-gray-500 mt-1">Manage and track all leads</p>
        </div>
        <button className="btn-primary text-sm" onClick={handleAddTest} disabled={createMutation.isPending}>
          {createMutation.isPending ? 'Adding…' : '+ Add Test Lead'}
        </button>
      </div>

      {/* Filters + Search */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-2">
          {FILTERS.map((f) => (
            <button
              key={f}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                filter === f
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
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
          className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-2 text-sm
                     focus:outline-none focus:border-violet-500 transition-colors placeholder:text-gray-600"
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" />
        </div>
      ) : error ? (
        <div className="card text-center py-10 text-red-400">Failed to load leads</div>
      ) : !data?.leads?.length ? (
        <div className="card text-center py-16">
          <p className="text-gray-500 text-lg">No leads found</p>
          <p className="text-gray-600 text-sm mt-2">Add a test lead or seed demo data from the Dashboard</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800 bg-gray-900/50">
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
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer"
                    onClick={() => nav(`/calls?lead_id=${lead.id}`)}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center text-xs font-bold shrink-0">
                          {lead.name?.charAt(0)}
                        </div>
                        <span className="font-medium">{lead.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-400">{lead.phone}</td>
                    <td className="py-3 px-4 text-gray-400">{lead.language}</td>
                    <td className="py-3 px-4 text-gray-400">{lead.source}</td>
                    <td className="py-3 px-4">
                      <ScoreBadge classification={lead.status?.includes('hot') ? 'hot' : lead.status?.includes('warm') ? 'warm' : lead.status === 'cold' ? 'cold' : 'pending'} />
                    </td>
                    <td className="py-3 px-4 text-gray-500 text-xs">{lead.created_at ? new Date(lead.created_at).toLocaleDateString() : '—'}</td>
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
