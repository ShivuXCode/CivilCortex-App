import { useState, useRef, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Home, Building2, ClipboardCheck, AlertTriangle, FileText, LogOut, Users, Settings, ChevronUp } from 'lucide-react';
import { cn } from '../components/ui';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/dashboard', icon: Home },
  { name: 'Buildings', path: '/buildings', icon: Building2 },
  { name: 'Inspections', path: '/inspections', icon: ClipboardCheck },
  { name: 'Defects', path: '/defects', icon: AlertTriangle },
  { name: 'Team', path: '/team', icon: Users },
  { name: 'Reports', path: '/reports', icon: FileText },
];

export const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800">
          <span className="text-xl font-bold text-white tracking-tight">CivilCortex</span>
        </div>
        
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-slate-800 text-white" 
                    : "hover:bg-slate-800 hover:text-white"
                )
              }
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>
        
        <div className="p-4 border-t border-slate-800 relative" ref={dropdownRef}>
          <button 
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-3 w-full px-2 py-2 rounded-md hover:bg-slate-800 transition-colors"
          >
            <div className="h-8 w-8 rounded-full bg-slate-700 flex flex-shrink-0 items-center justify-center text-white font-bold text-sm">
              {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-sm font-medium text-white truncate">{user?.full_name || user?.email}</p>
              {user?.full_name && <p className="text-xs text-slate-400 truncate">{user?.email}</p>}
            </div>
            <ChevronUp className={cn("h-4 w-4 text-slate-400 transition-transform", isDropdownOpen && "rotate-180")} />
          </button>

          {isDropdownOpen && (
            <div className="absolute bottom-full left-4 right-4 mb-2 bg-slate-800 rounded-md shadow-lg border border-slate-700 overflow-hidden z-50">
              <button
                onClick={() => {
                  setIsDropdownOpen(false);
                  navigate('/settings');
                }}
                className="flex w-full items-center gap-3 px-4 py-3 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <Settings className="h-4 w-4" />
                Settings
              </button>
              <div className="h-px bg-slate-700" />
              <button
                onClick={() => {
                  setIsDropdownOpen(false);
                  logout();
                }}
                className="flex w-full items-center gap-3 px-4 py-3 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-8">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
};
