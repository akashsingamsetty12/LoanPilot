import React from 'react';
import { classNames } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon: Icon,
  children,
  className,
  disabled,
  style,
  ...props
}: ButtonProps) {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-40 disabled:cursor-not-allowed';

  const resolvedVariant = variant === 'outline' ? 'secondary' : variant;

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  const iconSizes = {
    sm: 'h-3.5 w-3.5',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };

  // Build inline style per variant for the dark theme
  const variantStyle: React.CSSProperties =
    resolvedVariant === 'primary'
      ? {
          background: '#AAFF00',
          color: '#0A0A0A',
          boxShadow: '0 0 16px rgba(170,255,0,0.25)',
        }
      : resolvedVariant === 'secondary'
      ? {
          background: '#1A1A1A',
          color: '#A0A0A0',
          border: '1px solid rgba(255,255,255,0.08)',
        }
      : resolvedVariant === 'ghost'
      ? { color: '#666666' }
      : resolvedVariant === 'danger'
      ? {
          background: '#FF453A',
          color: '#FFFFFF',
          boxShadow: '0 0 12px rgba(255,69,58,0.25)',
        }
      : {};

  const focusRing =
    resolvedVariant === 'primary'
      ? 'focus:ring-primary-300/50 focus:ring-offset-surface-50'
      : resolvedVariant === 'danger'
      ? 'focus:ring-red-500/40 focus:ring-offset-surface-50'
      : 'focus:ring-white/10 focus:ring-offset-surface-50';

  const hoverClass =
    resolvedVariant === 'primary'
      ? 'hover:brightness-110 active:brightness-90'
      : resolvedVariant === 'secondary'
      ? 'hover:bg-surface-300 hover:text-charcoal'
      : resolvedVariant === 'ghost'
      ? 'hover:bg-white/[0.04] hover:text-charcoal'
      : resolvedVariant === 'danger'
      ? 'hover:brightness-110'
      : '';

  return (
    <button
      className={classNames(baseStyles, sizes[size], focusRing, hoverClass, className)}
      style={{ ...variantStyle, ...style }}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <svg
          className={`animate-spin ${iconSizes[size]}`}
          viewBox="0 0 24 24"
          fill="none"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : Icon ? (
        <Icon className={iconSizes[size]} />
      ) : null}
      {children}
    </button>
  );
}
