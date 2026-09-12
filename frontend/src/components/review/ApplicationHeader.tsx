import { FileText } from 'lucide-react';
import type { Application } from '../../types';
import { StatusBadge, RiskBadge } from '../applications/StatusBadge';
import { formatDateTime } from '../../lib/utils';

interface ApplicationHeaderProps {
  application: Application;
}

export function ApplicationHeader({ application }: ApplicationHeaderProps) {
  const completedDocs = application.documents.filter(d => d.status === 'completed').length;

  return (
    <div className="bg-white border border-surface-300 rounded-lg p-6 shadow-card">
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        {/* Left side */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
              <FileText className="h-5 w-5 text-primary-600" strokeWidth={1.8} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-charcoal">{application.applicant_name}</h2>
              <p className="text-sm text-charcoal-muted">{application.application_id} · {application.loan_type}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm">
            <StatusBadge status={application.status} />
            <span className="text-charcoal-muted">·</span>
            <span className="text-charcoal-muted">{completedDocs}/{application.documents.length} documents processed</span>
            <span className="text-charcoal-muted">·</span>
            <span className="text-charcoal-muted">Updated {formatDateTime(application.updated_at)}</span>
          </div>
        </div>

        {/* Right side: Risk */}
        <div className="flex items-center gap-4 md:text-right">
          <div>
            <p className="text-xs text-charcoal-muted uppercase tracking-wider mb-1">Risk Score</p>
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold text-charcoal tabular-nums">{application.risk.score}</span>
              <span className="text-sm text-charcoal-muted">/100</span>
            </div>
          </div>
          <div className="w-px h-12 bg-surface-300" />
          <div>
            <p className="text-xs text-charcoal-muted uppercase tracking-wider mb-1">Risk Level</p>
            <RiskBadge level={application.risk.level} />
          </div>
        </div>
      </div>
    </div>
  );
}
