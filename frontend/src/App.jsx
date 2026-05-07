import { Routes, Route, NavLink, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Leads from './pages/Leads';
import CallDetail from './pages/CallDetail';
import RMQueue from './pages/RMQueue';
import LandingPage from './pages/LandingPage';

const NAV_ICONS = {
  dashboard: (
    <svg fill="none" height="20" width="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>
      <rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
    </svg>
  ),
  leads: (
    <svg fill="none" height="20" width="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
      <path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  ),
  calls: (
    <svg fill="none" height="20" width="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.362 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
    </svg>
  ),
  rmQueue: (
    <svg fill="none" height="20" width="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
    </svg>
  ),
  home: (
    <svg fill="none" height="20" width="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  settings: (
    <svg fill="none" height="20" width="20" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  ),
};

const NAV_ITEMS = [
  { to: '/dashboard',       icon: NAV_ICONS.dashboard, label: 'Dashboard' },
  { to: '/dashboard/leads', icon: NAV_ICONS.leads,     label: 'Leads' },
  { to: '/dashboard/calls', icon: NAV_ICONS.calls,     label: 'Calls' },
  { to: '/dashboard/rm-queue', icon: NAV_ICONS.rmQueue, label: 'RM Queue' },
];

function DashboardLayout() {
  return (
    <div className="min-h-screen bg-[#A9B3AD] flex items-center justify-center p-4 sm:p-6">
      <div className="bg-[#F2F4F2] w-full max-w-[1440px] min-h-[90vh] rounded-[2.5rem] p-4 flex gap-4 overflow-hidden shadow-2xl relative">
        {/* Sidebar */}
        <aside className="w-[80px] bg-[#141416] rounded-[2rem] flex flex-col items-center py-6 justify-between shrink-0">
          {/* Top */}
          <div className="flex flex-col items-center gap-6 w-full">
            {/* Logo */}
            <Link to="/" className="w-11 h-11 rounded-2xl bg-[#232325] border border-gray-700 flex items-center justify-center text-[#EBF981] hover:bg-gray-700 transition" title="Home">
              {NAV_ICONS.rmQueue}
            </Link>
            {/* Home link */}
            <Link to="/" className="text-gray-400 hover:text-white transition flex justify-center w-full">
              {NAV_ICONS.home}
            </Link>
            {/* Nav icons */}
            <nav className="flex flex-col gap-2 items-center w-full mt-2">
              {NAV_ITEMS.map(({ to, icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/dashboard'}
                  title={label}
                  className={({ isActive }) =>
                    `w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-200 relative ${
                      isActive
                        ? 'bg-[#2C2C2F] text-white'
                        : 'text-gray-500 hover:text-white'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {icon}
                      {isActive && (
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-white rounded-r-md" />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
          {/* Bottom */}
          <div className="flex flex-col items-center gap-4 w-full">
            <button className="text-gray-500 hover:text-white transition" title="Settings">
              {NAV_ICONS.settings}
            </button>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#EBF981] to-[#a3c44d] flex items-center justify-center text-[#141416] font-bold text-sm">
              R
            </div>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto pr-2 pt-2 pb-2 dashboard-scroll">
          <Routes>
            <Route index element={<Dashboard />} />
            <Route path="leads" element={<Leads />} />
            <Route path="calls" element={<CallDetail />} />
            <Route path="rm-queue" element={<RMQueue />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/dashboard/*" element={<DashboardLayout />} />
    </Routes>
  );
}
