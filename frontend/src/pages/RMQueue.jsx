import { useRmQueue, useUpdateRmStatus } from '../hooks/useLeads';

export default function RMQueue() {
  const { data, isLoading, error } = useRmQueue();
  const updateMutation = useUpdateRmStatus();

  const handleStatusChange = (id, status) => {
    updateMutation.mutate({ id, status });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
          RM Queue
        </h1>
        <p className="text-sm text-gray-500 mt-1">Hot leads awaiting relationship manager action</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" />
        </div>
      ) : error ? (
        <div className="card text-center py-10 text-red-400">Failed to load RM queue</div>
      ) : !data?.queue?.length ? (
        <div className="card text-center py-16">
          <p className="text-gray-500 text-lg">No hot leads in queue</p>
          <p className="text-gray-600 text-sm mt-2">Hot leads will appear here after call scoring</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800 bg-gray-900/50">
                  <th className="text-left py-3 px-4">Lead</th>
                  <th className="text-left py-3 px-4">Phone</th>
                  <th className="text-left py-3 px-4">Score</th>
                  <th className="text-left py-3 px-4">Objections</th>
                  <th className="text-left py-3 px-4">Time in Queue</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.queue.map((item) => {
                  const queuedAt = item.queued_at ? new Date(item.queued_at) : null;
                  const elapsed = queuedAt ? Math.round((Date.now() - queuedAt.getTime()) / 60000) : 0;

                  return (
                    <tr key={item.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center text-xs font-bold">
                            {item.lead_name?.charAt(0)}
                          </div>
                          <span className="font-medium">{item.lead_name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-400">{item.phone}</td>
                      <td className="py-3 px-4">
                        <span className="badge-hot">{item.score}</span>
                      </td>
                      <td className="py-3 px-4 text-gray-400 text-xs">
                        {item.objections_raised?.join(', ') || 'None'}
                      </td>
                      <td className="py-3 px-4 text-gray-400">
                        {elapsed < 60 ? `${elapsed}m` : `${Math.round(elapsed / 60)}h`}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          item.rm_status === 'pending' ? 'bg-yellow-500/15 text-yellow-300' :
                          item.rm_status === 'called' ? 'bg-blue-500/15 text-blue-300' :
                          item.rm_status === 'converted' ? 'bg-emerald-500/15 text-emerald-300' :
                          'bg-red-500/15 text-red-300'
                        }`}>{item.rm_status}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-1">
                          {item.rm_status === 'pending' && (
                            <button
                              className="text-xs px-2 py-1 bg-blue-600/20 text-blue-300 rounded-lg hover:bg-blue-600/30 transition"
                              onClick={() => handleStatusChange(item.id, 'called')}
                            >
                              Mark Called
                            </button>
                          )}
                          {(item.rm_status === 'pending' || item.rm_status === 'called') && (
                            <>
                              <button
                                className="text-xs px-2 py-1 bg-emerald-600/20 text-emerald-300 rounded-lg hover:bg-emerald-600/30 transition"
                                onClick={() => handleStatusChange(item.id, 'converted')}
                              >
                                Converted
                              </button>
                              <button
                                className="text-xs px-2 py-1 bg-red-600/20 text-red-300 rounded-lg hover:bg-red-600/30 transition"
                                onClick={() => handleStatusChange(item.id, 'lost')}
                              >
                                Lost
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
