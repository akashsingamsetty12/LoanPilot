import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="min-h-screen" style={{ background: '#0A0A0A' }}>
      <Sidebar />
      <div className="ml-[240px] min-h-screen transition-all duration-300">
        <Outlet />
      </div>
    </div>
  );
}
