import { classNames } from '../../lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({ children, variant = 'default', size = 'sm', className }: BadgeProps) {
  const variants = {
    default: 'bg-surface-200 text-charcoal-secondary border-surface-300',
    success: 'bg-risk-low-bg text-risk-low border-risk-low-border',
    warning: 'bg-risk-medium-bg text-risk-medium border-risk-medium-border',
    danger: 'bg-risk-high-bg text-risk-high border-risk-high-border',
    info: 'bg-primary-50 text-primary-700 border-primary-200',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  };

  return (
    <span
      className={classNames(
        'inline-flex items-center font-medium rounded border',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}
