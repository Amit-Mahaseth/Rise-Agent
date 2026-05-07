import { useRmQueue, useUpdateRmStatus } from '../hooks/useLeads';

export default function RMQueue() {
  const { data, isLoading, error } = useRmQueue();
  const updateMutation = useUpdateRmStatus();

  const handleStatusChange = (id, status) => {
    updateMutation.mutate({ id, status });
  };

  return (
    <div className="space-y-5 px-1 pt-2">
      <div>
        <h1 className="text-3xl font-medium text-[#141416]">RM Queue</h1>
        <p className="text-sm text-gray-500 mt-1">Hot leads awaiting relationship manager action</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin w-8 h-8 border-2 border-[#141416] border-t-transparent rounded-full" />
        </div>
      ) : error ? (
        <div className="bg-white rounded-[2rem] p-10 text-center shadow-soft text-red-500">Failed to load RM queue</div>
      ) : !data?.queue?.length ? (
        <div className="bg-white rounded-[2rem] p-16 text-center shadow-soft">
          <p className="text-gray-500 text-lg">No hot leads in queue</p>
          <p className="text-gray-400 text-sm mt-2">Hot leads will appear here after call scoring</p>
        </div>
      ) : (
        <div className="bg-white rounded-[2rem] overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.05)]">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-400 uppercase tracking-wider border-b border-gray-100 bg-gray-50/50">
                  <th className="text-left py-3 px-4">Lead</th>
                  <th className="text-left py-3 px-4">Phone</th>
                  <th className="text-left py-3 px-4">Score</th>
                  <th className="text-left py-3 px-4">Objections</th>
                  <th className="text-left py-3 px-4">Time</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.queue.map((item) => {
                  const queuedAt = item.queued_at ? new Date(item.queued_at) : null;
                  const elapsed = queuedAt ? Math.round((Date.now() - queuedAt.getTime()) / 60000) : 0;

                  return (
                    <tr key={item.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-xs font-bold text-red-600">
                            {item.lead_name?.charAt(0)}
                          </div>
                          <span className="font-medium text-[#141416]">{item.lead_name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-500">{item.phone}</td>
                      <td className="py-3 px-4">
                        <span className="bg-red-50 text-red-600 border border-red-200 text-xs px-2.5 py-1 rounded-full font-bold">
                          🔥 {item.score}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-xs">{item.objections_raised?.join(', ') || 'None'}</td>
                      <td className="py-3 px-4 text-gray-500">{elapsed < 60 ? `${elapsed}m` : `${Math.round(elapsed / 60)}h`}</td>
                      <td className="py-3 px-4">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium border ${
                          item.rm_status === 'pending' ? 'bg-amber-50 text-amber-600 border-amber-200' :
                          item.rm_status === 'called' ? 'bg-blue-50 text-blue-600 border-blue-200' :
                          item.rm_status === 'converted' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' :
                          'bg-red-50 text-red-600 border-red-200'
                        }`}>{item.rm_status}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-1.5">
                          {item.rm_status === 'pending' && (
                            <button
                              className="text-xs px-3 py-1.5 bg-blue-50 text-blue-600 rounded-full hover:bg-blue-100 transition border border-blue-200 font-medium"
                              onClick={() => handleStatusChange(item.id, 'called')}
                            >Called</button>
                          )}
                          {(item.rm_status === 'pending' || item.rm_status === 'called') && (
                            <>
                              <button
                                className="text-xs px-3 py-1.5 bg-emerald-50 text-emerald-600 rounded-full hover:bg-emerald-100 transition border border-emerald-200 font-medium"
                                onClick={() => handleStatusChange(item.id, 'converted')}
                              >Won</button>
                              <button
                                className="text-xs px-3 py-1.5 bg-red-50 text-red-600 rounded-full hover:bg-red-100 transition border border-red-200 font-medium"
                                onClick={() => handleStatusChange(item.id, 'lost')}
                              >Lost</button>
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
