import { classNames } from '../../lib/utils';

interface ConfidenceIndicatorProps {
  value: number;
  showLabel?: boolean;
  size?: 'sm' | 'md';
}

export function ConfidenceIndicator({ value, showLabel = true, size = 'sm' }: ConfidenceIndicatorProps) {
  const getColor = (v: number) => {
    if (v >= 90) return 'bg-risk-low';
    if (v >= 75) return 'bg-risk-medium';
    return 'bg-risk-high';
  };

  const getTextColor = (v: number) => {
    if (v >= 90) return 'text-risk-low';
    if (v >= 75) return 'text-risk-medium';
    return 'text-risk-high';
  };

  const heights = { sm: 'h-1.5', md: 'h-2' };

  return (
    <div className="flex items-center gap-2">
      <div className={classNames('flex-1 bg-surface-200 rounded-full overflow-hidden min-w-[40px] max-w-[60px]', heights[size])}>
        <div
          className={classNames('h-full rounded-full transition-all duration-300', getColor(value))}
          style={{ width: `${value}%` }}
        />
      </div>
      {showLabel && (
        <span className={classNames('text-xs font-medium tabular-nums', getTextColor(value))}>
          {value}%
        </span>
      )}
    </div>
  );
}
