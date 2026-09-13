import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderPlus,
  FileText,
  BarChart3,
  Settings,
  User,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/applications/new', icon: FolderPlus, label: 'New Application' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={`fixed top-0 left-0 h-screen bg-white border-r border-surface-300 flex flex-col z-30 transition-all duration-200 ${
        collapsed ? 'w-[68px]' : 'w-[240px]'
      }`}
    >
      {/* Logo */}
      <div className="flex items-center h-[56px] px-4 border-b border-surface-300">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center flex-shrink-0">
            <FileText className="h-4 w-4 text-white" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <span className="text-base font-bold text-charcoal tracking-tight">LoanIQ</span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2.5 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => {
          const isActive = to === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(to);

          return (
            <NavLink
              key={to}
              to={to}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150 ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-charcoal-secondary hover:bg-surface-100 hover:text-charcoal'
              }`}
              title={collapsed ? label : undefined}
            >
              <Icon className="h-[18px] w-[18px] flex-shrink-0" strokeWidth={1.8} />
              {!collapsed && <span className="truncate">{label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="border-t border-surface-300 p-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-surface-200 flex items-center justify-center flex-shrink-0">
            <User className="h-4 w-4 text-charcoal-muted" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-medium text-charcoal truncate">Loan Officer</p>
              <p className="text-xs text-charcoal-muted truncate">Verification Team</p>
            </div>
          )}
        </div>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute top-[68px] -right-3 w-6 h-6 bg-white border border-surface-300 rounded-full flex items-center justify-center text-charcoal-muted hover:text-charcoal hover:bg-surface-100 transition-colors shadow-sm"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </button>
    </aside>
  );
}
