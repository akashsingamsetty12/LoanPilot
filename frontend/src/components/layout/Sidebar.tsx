import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderPlus,
  BarChart3,
  Settings,
  User,
  ChevronLeft,
  ChevronRight,
  Zap,
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
      className={`fixed top-0 left-0 h-screen flex flex-col z-30 transition-all duration-300 ${
        collapsed ? 'w-[68px]' : 'w-[240px]'
      }`}
      style={{
        background: '#0D0D0D',
        borderRight: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center h-[60px] px-4 flex-shrink-0"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          {/* Logo mark */}
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: '#AAFF00', boxShadow: '0 0 16px rgba(170,255,0,0.4)' }}
          >
            <Zap className="h-4 w-4" style={{ color: '#0A0A0A' }} strokeWidth={2.5} />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <span className="text-base font-bold tracking-tight" style={{ color: '#F0F0F0' }}>
                LoanPilot
              </span>
              <div
                className="text-[10px] font-medium tracking-widest uppercase"
                style={{ color: '#AAFF00', marginTop: '-2px' }}
              >
                AI Platform
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => {
          const isActive =
            to === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(to);

          return (
            <NavLink
              key={to}
              to={to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive ? 'nav-active-glow' : 'hover:bg-white/[0.04]'
              }`}
              style={
                isActive
                  ? {
                      background: 'rgba(170,255,0,0.1)',
                      color: '#AAFF00',
                      border: '1px solid rgba(170,255,0,0.15)',
                    }
                  : {
                      color: '#666666',
                      border: '1px solid transparent',
                    }
              }
              title={collapsed ? label : undefined}
            >
              <Icon
                className="flex-shrink-0"
                style={{ width: 17, height: 17 }}
                strokeWidth={isActive ? 2.2 : 1.8}
              />
              {!collapsed && <span className="truncate">{label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* User Profile */}
      <div
        className="p-3 flex-shrink-0"
        style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
            style={{ background: '#1A1A1A', border: '1px solid rgba(255,255,255,0.1)' }}
          >
            <User className="h-4 w-4" style={{ color: '#666666' }} />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-sm font-medium truncate" style={{ color: '#F0F0F0' }}>
                Loan Officer
              </p>
              <p className="text-xs truncate" style={{ color: '#555555' }}>
                Verification Team
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute top-[70px] -right-3 w-6 h-6 rounded-full flex items-center justify-center transition-all duration-150 hover:scale-110"
        style={{
          background: '#1A1A1A',
          border: '1px solid rgba(255,255,255,0.1)',
          color: '#555555',
        }}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </button>
    </aside>
  );
}
