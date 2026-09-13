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
    <div className={classNames('border rounded-lg overflow-hidden', c.border)}>
      <div className={classNames('px-5 py-4', c.bg)}>
        <div className="flex items-center gap-3">
          <span className={c.iconColor}>{c.icon}</span>
          <div>
            <h3 className={classNames('text-base font-semibold', c.text)}>{c.label}</h3>
            <p className="text-sm text-charcoal-secondary mt-0.5">{c.description}</p>
          </div>
        </div>
      </div>
      <div className="bg-white px-5 py-3 border-t border-surface-200">
        <div className="flex items-start gap-2">
          <Info className="h-3.5 w-3.5 text-charcoal-muted mt-0.5 flex-shrink-0" />
          <p className="text-xs text-charcoal-muted">
            The final lending decision belongs to the human loan officer. LoanIQ provides AI-assisted analysis but does not make approval or rejection decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
