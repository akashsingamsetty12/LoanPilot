export function Spinner({
  size = 'md',
  className = '',
  text,
}: {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  text?: string;
}) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <svg
        className={`animate-spin ${sizes[size]} ${className}`}
        style={{ color: '#AAFF00' }}
        viewBox="0 0 24 24"
        fill="none"
        aria-label="Loading"
      >
        <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      {text && <p className="mt-3 text-xs font-medium" style={{ color: '#444444' }}>{text}</p>}
    </div>
  );
}

export function LoadingState({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <Spinner size="lg" text={message} />
    </div>
  );
}
