interface TopbarProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
}

export function Topbar({ title, subtitle, children }: TopbarProps) {
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
      <div className="flex items-center gap-3">
        {children}

        {/* Status pill */}
        <div
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
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
