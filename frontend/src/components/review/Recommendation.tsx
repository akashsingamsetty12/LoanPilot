import { ShieldCheck, ShieldAlert, ShieldQuestion, Info } from 'lucide-react';
import type { Recommendation as RecommendationType } from '../../types';
import { classNames } from '../../lib/utils';

interface RecommendationProps {
  recommendation: RecommendationType;
}

const config: Record<RecommendationType, {
  icon: React.ReactNode;
  label: string;
  description: string;
  bg: string;
  border: string;
  text: string;
  iconColor: string;
}> = {
  NEEDS_HUMAN_REVIEW: {
    icon: <ShieldAlert className="h-5 w-5" />,
    label: 'Needs Human Review',
    description: 'This application requires manual review by an authorized loan officer before a lending decision can be made.',
    bg: 'bg-risk-medium-bg',
    border: 'border-risk-medium-border',
    text: 'text-risk-medium',
    iconColor: 'text-risk-medium',
  },
  APPROVE: {
    icon: <ShieldCheck className="h-5 w-5" />,
    label: 'Recommended for Approval',
    description: 'All verification checks passed. Final approval must be granted by an authorized loan officer.',
    bg: 'bg-risk-low-bg',
    border: 'border-risk-low-border',
    text: 'text-risk-low',
    iconColor: 'text-risk-low',
  },
  REJECT: {
    icon: <ShieldAlert className="h-5 w-5" />,
    label: 'Recommended for Rejection',
    description: 'Significant issues were identified. Final decision must be made by an authorized loan officer.',
    bg: 'bg-risk-high-bg',
    border: 'border-risk-high-border',
    text: 'text-risk-high',
    iconColor: 'text-risk-high',
  },
  INSUFFICIENT_DATA: {
    icon: <ShieldQuestion className="h-5 w-5" />,
    label: 'Insufficient Data',
    description: 'Not enough documents or information to make a recommendation. Additional documents are required.',
    bg: 'bg-surface-100',
    border: 'border-surface-300',
    text: 'text-charcoal-secondary',
    iconColor: 'text-charcoal-muted',
  },
};

export function Recommendation({ recommendation }: RecommendationProps) {
  const c = config[recommendation];

  return (
    <div
      className={classNames('rounded-xl overflow-hidden border', c.border)}
      style={{
        boxShadow: '0 1px 3px rgba(0,0,0,0.5)',
      }}
    >
      <div className={classNames('px-5 py-4', c.bg)}>
        <div className="flex items-center gap-3">
          <span className={c.iconColor}>{c.icon}</span>
          <div>
            <h3 className={classNames('text-base font-semibold', c.text)}>{c.label}</h3>
            <p className="text-sm mt-0.5" style={{ color: '#A0A0A0' }}>{c.description}</p>
          </div>
        </div>
      </div>
      <div
        className="px-5 py-3 flex items-start gap-2"
        style={{
          background: '#0D0D0D',
          borderTop: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <Info className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" style={{ color: '#555555' }} />
        <p className="text-xs" style={{ color: '#666666' }}>
          The final lending decision belongs to the authorized human loan officer. LoanPilot provides AI-assisted analysis and risk flags.
        </p>
      </div>
    </div>
  );
}
