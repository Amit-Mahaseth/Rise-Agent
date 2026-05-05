export default function TranscriptView({ events }) {
  if (!events || events.length === 0) {
    return <p className="text-gray-500 text-sm italic">No transcript available.</p>;
  }

  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
      {events.map((ev, i) => {
        const isAgent = ev.speaker === 'agent';
        return (
          <div key={ev.id || i} className={`flex ${isAgent ? 'justify-start' : 'justify-end'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
                ${isAgent
                  ? 'bg-violet-600/15 text-violet-200 border border-violet-500/20 rounded-bl-md'
                  : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-br-md'
                }`}
            >
              <p className={`text-[10px] font-semibold uppercase tracking-wider mb-1 ${isAgent ? 'text-violet-400' : 'text-gray-500'}`}>
                {isAgent ? '🤖 Agent' : '👤 Lead'} · Turn {ev.turn_number}
              </p>
              <p>{ev.text}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
