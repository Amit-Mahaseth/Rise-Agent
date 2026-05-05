import { useSearchParams } from 'react-router-dom';
import { useCallDetail } from '../hooks/useLeads';
import { useQuery } from '@tanstack/react-query';
import { getCalls } from '../lib/api';
import ScoreBadge from '../components/ScoreBadge';
import TranscriptView from '../components/TranscriptView';

export default function CallDetail() {
  const [params] = useSearchParams();
  const leadId = params.get('lead_id');
  const callId = params.get('call_id');

  // If we have a call_id, load that call. Otherwise list calls for the lead.
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
        <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" />
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="card text-center py-10">
        <p className="text-gray-500">
          {error ? `Error: ${error.message}` : 'Select a call to view details. Navigate here from the Leads page.'}
        </p>
      </div>
    );
  }

  const { call, events, score, lead } = data;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
        Call Detail
      </h1>

      {/* Lead Info Header */}
      {lead && (
        <div className="card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center text-xl font-bold">
              {lead.name?.charAt(0)}
            </div>
            <div>
              <h2 className="text-lg font-semibold">{lead.name}</h2>
              <p className="text-sm text-gray-400">{lead.phone} · {lead.language}</p>
            </div>
          </div>
          {score && <ScoreBadge classification={score.classification} score={score.total_score} />}
        </div>
      )}

      {/* Call Meta */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Duration', value: `${call.duration_seconds}s` },
          { label: 'Status', value: call.status },
          { label: 'Language', value: call.language_used || lead?.language || '—' },
          { label: 'Call #', value: call.call_number },
        ].map(({ label, value }) => (
          <div key={label} className="card-sm text-center">
            <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
            <p className="text-lg font-semibold mt-1">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transcript */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Conversation Transcript
          </h3>
          <TranscriptView events={events} />
        </div>

        {/* Score Breakdown */}
        {score && (
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
              Score Breakdown
            </h3>
            <div className="space-y-3">
              {[
                { label: 'Verbal Intent', value: score.verbal_intent ? 'Yes (+40)' : 'No (0)', highlight: score.verbal_intent },
                { label: 'Objections', value: `${score.objection_count} (${score.objection_count > 0 ? '-' + score.objection_count * 10 : '0'})`, highlight: false },
                { label: 'Duration Score', value: `+${score.duration_score}`, highlight: score.duration_score > 0 },
                { label: 'Network Mentioned', value: score.network_mentioned ? 'Yes (+15)' : 'No (0)', highlight: score.network_mentioned },
                { label: 'Tone Score', value: `${score.tone_score}/2 (+${score.tone_score * 5})`, highlight: score.tone_score > 0 },
              ].map(({ label, value, highlight }) => (
                <div key={label} className="flex justify-between items-center py-2 border-b border-gray-800/50">
                  <span className="text-gray-400 text-sm">{label}</span>
                  <span className={`text-sm font-medium ${highlight ? 'text-emerald-400' : 'text-gray-300'}`}>{value}</span>
                </div>
              ))}
              <div className="flex justify-between items-center pt-2">
                <span className="font-semibold">Total Score</span>
                <span className="text-xl font-bold">{score.total_score}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
