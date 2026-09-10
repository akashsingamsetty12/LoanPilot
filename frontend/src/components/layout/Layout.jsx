/**
 * Layout Component
 * =====================================
 * App shell with sidebar navigation, header, and main content area.
 *
 * TODO: Implement responsive layout with Tailwind
 */

import { Outlet, Link, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/applications/new', label: 'New Application', icon: '➕' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 p-4">
        <div className="mb-8">
          <h1 className="text-xl font-bold text-blue-600">🏦 LoanPilot</h1>
          <p className="text-xs text-gray-500">AI Document Verification</p>
        </div>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-3 py-2 rounded-lg text-sm ${
                location.pathname === item.path
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {item.icon} {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
