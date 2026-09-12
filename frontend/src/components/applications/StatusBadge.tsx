import type { ApplicationStatus, RiskLevel } from '../../types';
import { getStatusLabel, getStatusColor, classNames } from '../../lib/utils';

interface StatusBadgeProps {
  status: ApplicationStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const colors = getStatusColor(status);
  return (
    <span
      className={classNames(
        'inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium rounded border',
        colors.text,
        colors.bg,
        colors.border
      )}
    >
      <span className={classNames('w-1.5 h-1.5 rounded-full', getStatusDot(status))} />
      {getStatusLabel(status)}
    </span>
  );
}

function getStatusDot(status: ApplicationStatus): string {
  const map: Record<ApplicationStatus, string> = {
    draft: 'bg-charcoal-muted',
    uploading: 'bg-primary-500 animate-pulse',
    processing: 'bg-primary-500 animate-pulse',
    review: 'bg-risk-medium',
    completed: 'bg-risk-low',
    rejected: 'bg-risk-high',
  };
  return map[status];
}

interface RiskBadgeProps {
  level: RiskLevel;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  const colors: Record<RiskLevel, { text: string; bg: string; border: string }> = {
    HIGH: { text: 'text-risk-high', bg: 'bg-risk-high-bg', border: 'border-risk-high-border' },
    MEDIUM: { text: 'text-risk-medium', bg: 'bg-risk-medium-bg', border: 'border-risk-medium-border' },
    LOW: { text: 'text-risk-low', bg: 'bg-risk-low-bg', border: 'border-risk-low-border' },
    PASS: { text: 'text-risk-pass', bg: 'bg-risk-pass-bg', border: 'border-risk-pass-border' },
  };

  const c = colors[level];
  return (
    <span className={classNames('inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded border', c.text, c.bg, c.border)}>
      {level}
    </span>
  );
}
