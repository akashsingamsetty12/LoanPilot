import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="min-h-screen bg-surface-100">
      <Sidebar />
      <div className="ml-[240px] min-h-screen transition-all duration-200">
        <Outlet />
      </div>
    </div>
  );
}
