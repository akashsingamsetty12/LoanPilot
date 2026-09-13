import { Bell, Search, X } from 'lucide-react';
import { useState } from 'react';

interface TopbarProps {
  title: string;
  subtitle?: string;
}

export function Topbar({ title, subtitle }: TopbarProps) {
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <header
      className="h-[60px] flex items-center justify-between px-6 sticky top-0 z-20"
      style={{
        background: 'rgba(11,11,11,0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      {/* Left: Title */}
      <div className="min-w-0">
        <h1 className="text-base font-semibold truncate" style={{ color: '#F0F0F0' }}>
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs truncate -mt-0.5" style={{ color: '#555555' }}>
            {subtitle}
          </p>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        {searchOpen ? (
          <div className="relative flex items-center">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5"
              style={{ color: '#555555' }}
            />
            <input
              type="text"
              placeholder="Search applications..."
              className="pl-9 pr-9 py-2 text-sm rounded-lg w-56 focus:outline-none focus:ring-2"
              style={{
                background: '#1A1A1A',
                border: '1px solid rgba(170,255,0,0.3)',
                color: '#F0F0F0',
                boxShadow: '0 0 12px rgba(170,255,0,0.08)',
              }}
              autoFocus
              onBlur={() => setSearchOpen(false)}
              aria-label="Search applications"
            />
            <button
              className="absolute right-2.5 top-1/2 -translate-y-1/2"
              style={{ color: '#555555' }}
              onMouseDown={() => setSearchOpen(false)}
              tabIndex={-1}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => setSearchOpen(true)}
            className="p-2 rounded-lg transition-all duration-150 hover:bg-white/[0.04]"
            style={{ color: '#555555' }}
            aria-label="Open search"
          >
            <Search className="h-[17px] w-[17px]" strokeWidth={1.8} />
          </button>
        )}

        {/* Notifications */}
        <button
          className="p-2 rounded-lg transition-all duration-150 hover:bg-white/[0.04] relative"
          style={{ color: '#555555' }}
          aria-label="Notifications"
        >
          <Bell className="h-[17px] w-[17px]" strokeWidth={1.8} />
          <span
            className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full"
            style={{ background: '#FF453A', boxShadow: '0 0 6px rgba(255,69,58,0.6)' }}
          />
        </button>

        {/* Status pill */}
        <div
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ml-1"
          style={{
            background: 'rgba(170,255,0,0.08)',
            border: '1px solid rgba(170,255,0,0.15)',
            color: '#AAFF00',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full animate-pulse"
            style={{ background: '#AAFF00' }}
          />
          AI Active
        </div>
      </div>
    </header>
  );
}
