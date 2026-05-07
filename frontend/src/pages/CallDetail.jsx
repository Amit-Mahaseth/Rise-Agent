import { useSearchParams } from 'react-router-dom';
import { useCallDetail } from '../hooks/useLeads';
import { useQuery } from '@tanstack/react-query';
import { getCalls } from '../lib/api';
import TranscriptView from '../components/TranscriptView';

export default function CallDetail() {
  const [params] = useSearchParams();
  const leadId = params.get('lead_id');
  const callId = params.get('call_id');

  const { data: callsData } = useQuery({
    queryKey: ['calls-list', leadId],
    queryFn: () => getCalls({ lead_id: leadId, limit: 10 }),
    enabled: !!leadId && !callId,
  });

  const effectiveCallId = callId || (callsData && callsData.length > 0 ? callsData[0].id : null);
  const { data, isLoading, error } = useCallDetail(effectiveCallId);

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <div className="animate-spin w-8 h-8 border-2 border-[#141416] border-t-transparent rounded-full" />
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="bg-white rounded-[2rem] p-10 text-center shadow-soft mx-1 mt-2">
        <p className="text-gray-500">
          {error ? `Error: ${error.message}` : 'Select a call to view details. Navigate here from the Leads page.'}
        </p>
      </div>
    );
  }

  const { call, events, score, lead } = data;

  return (
    <div className="space-y-5 px-1 pt-2">
      <h1 className="text-3xl font-medium text-[#141416]">Call Detail</h1>

      {lead && (
        <div className="bg-white rounded-[2rem] p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-[#141416] flex items-center justify-center text-xl font-bold text-white">
              {lead.name?.charAt(0)}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-[#141416]">{lead.name}</h2>
              <p className="text-sm text-gray-500">{lead.phone} · {lead.language}</p>
            </div>
          </div>
          {score && (
            <span className={`text-sm px-4 py-2 rounded-full font-bold ${
              score.classification === 'hot' ? 'bg-red-50 text-red-600 border border-red-200' :
              score.classification === 'warm' ? 'bg-amber-50 text-amber-600 border border-amber-200' :
              score.classification === 'cold' ? 'bg-blue-50 text-blue-600 border border-blue-200' :
              'bg-gray-50 text-gray-500 border border-gray-200'
            }`}>
              {score.classification?.toUpperCase()} · {score.total_score}
            </span>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Duration', value: `${call.duration_seconds}s` },
          { label: 'Status', value: call.status },
          { label: 'Language', value: call.language_used || lead?.language || '—' },
          { label: 'Call #', value: call.call_number },
        ].map(({ label, value }) => (
          <div key={label} className="bg-white rounded-2xl p-4 text-center shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
            <p className="text-xs text-gray-400 uppercase tracking-wider">{label}</p>
            <p className="text-lg font-semibold text-[#141416] mt-1">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-[2rem] p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Transcript</h3>
          <TranscriptView events={events} />
        </div>

        {score && (
          <div className="bg-white rounded-[2rem] p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Score Breakdown</h3>
            <div className="space-y-3">
              {[
                { label: 'Verbal Intent', value: score.verbal_intent ? 'Yes (+40)' : 'No (0)', highlight: score.verbal_intent },
                { label: 'Objections', value: `${score.objection_count} (${score.objection_count > 0 ? '-' + score.objection_count * 10 : '0'})`, highlight: false },
                { label: 'Duration Score', value: `+${score.duration_score}`, highlight: score.duration_score > 0 },
                { label: 'Network', value: score.network_mentioned ? 'Yes (+15)' : 'No (0)', highlight: score.network_mentioned },
                { label: 'Tone', value: `${score.tone_score}/2 (+${score.tone_score * 5})`, highlight: score.tone_score > 0 },
              ].map(({ label, value, highlight }) => (
                <div key={label} className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500 text-sm">{label}</span>
                  <span className={`text-sm font-medium ${highlight ? 'text-emerald-600' : 'text-[#141416]'}`}>{value}</span>
                </div>
              ))}
              <div className="flex justify-between items-center pt-2">
                <span className="font-semibold text-[#141416]">Total Score</span>
                <span className="text-xl font-bold text-[#141416]">{score.total_score}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
