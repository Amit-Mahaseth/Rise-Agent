import { Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Leads from './pages/Leads';
import CallDetail from './pages/CallDetail';
import RMQueue from './pages/RMQueue';

const NAV_ITEMS = [
  { to: '/',        label: 'Dashboard', icon: '📊' },
  { to: '/leads',   label: 'Leads',     icon: '👥' },
  { to: '/calls',   label: 'Calls',     icon: '📞' },
  { to: '/rm-queue',label: 'RM Queue',  icon: '🎯' },
];

export default function App() {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-600/20">
              <span className="text-lg">🚀</span>
            </div>
            <div>
              <h1 className="font-bold text-lg bg-gradient-to-r from-violet-300 to-indigo-300 bg-clip-text text-transparent">
                RiseAgent AI
              </h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest">Voice Agent</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-violet-600/15 text-violet-300 border border-violet-500/20'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <span>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800">
          <div className="card-sm bg-gradient-to-r from-violet-900/30 to-indigo-900/30 border-violet-800/30 text-center">
            <p className="text-[10px] text-gray-500 uppercase tracking-wider">Mode</p>
            <p className="text-xs font-semibold text-violet-300 mt-0.5">🟢 Demo Active</p>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6 lg:p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/calls" element={<CallDetail />} />
            <Route path="/rm-queue" element={<RMQueue />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
