import { Bell, Search } from 'lucide-react';
import { useState } from 'react';

interface TopbarProps {
  title: string;
  subtitle?: string;
}

export function Topbar({ title, subtitle }: TopbarProps) {
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <header className="h-[56px] bg-white border-b border-surface-300 flex items-center justify-between px-6 sticky top-0 z-20">
      {/* Left: Title */}
      <div className="min-w-0">
        <h1 className="text-lg font-semibold text-charcoal truncate">{title}</h1>
        {subtitle && (
          <p className="text-xs text-charcoal-muted truncate -mt-0.5">{subtitle}</p>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        {searchOpen ? (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-charcoal-muted" />
            <input
              type="text"
              placeholder="Search applications..."
              className="input-field pl-9 w-64"
              autoFocus
              onBlur={() => setSearchOpen(false)}
              aria-label="Search applications"
            />
          </div>
        ) : (
          <button
            onClick={() => setSearchOpen(true)}
            className="p-2 rounded-md hover:bg-surface-100 text-charcoal-muted transition-colors"
            aria-label="Open search"
          >
            <Search className="h-[18px] w-[18px]" strokeWidth={1.8} />
          </button>
        )}

        {/* Notifications */}
        <button
          className="p-2 rounded-md hover:bg-surface-100 text-charcoal-muted transition-colors relative"
          aria-label="Notifications"
        >
          <Bell className="h-[18px] w-[18px]" strokeWidth={1.8} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-risk-high rounded-full" />
        </button>
      </div>
    </header>
  );
}
