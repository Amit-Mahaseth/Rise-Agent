import { useNavigate } from 'react-router-dom';
import ScoreBadge from './ScoreBadge';

export default function LeadCard({ lead, score }) {
  const nav = useNavigate();
  const lang = lead.language || 'unknown';

  return (
    <div
      onClick={() => nav(`/leads`)}
      className="card-sm flex items-center justify-between cursor-pointer hover:border-gray-600
                 transition-all duration-300 hover:-translate-y-0.5 group"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center font-bold text-sm shrink-0">
          {lead.name?.charAt(0) || '?'}
        </div>
        <div className="min-w-0">
          <p className="font-medium text-sm truncate group-hover:text-white transition-colors">{lead.name}</p>
          <p className="text-xs text-gray-500">{lead.phone} · {lang}</p>
        </div>
      </div>
      <ScoreBadge classification={lead.status === 'pending' ? 'pending' : (score?.classification || lead.status)} score={score?.total_score} />
    </div>
  );
}
