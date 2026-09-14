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
    <div
      className="rounded-xl p-6 transition-all duration-200"
      style={{
        background: '#111111',
        border: '1px solid rgba(255,255,255,0.06)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.5)',
      }}
    >
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        {/* Left side */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: 'rgba(170,255,0,0.1)', border: '1px solid rgba(170,255,0,0.2)' }}
            >
              <FileText className="h-5 w-5" style={{ color: '#AAFF00' }} strokeWidth={1.8} />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight" style={{ color: '#F0F0F0' }}>
                {application.applicant_name}
              </h2>
              <p className="text-sm mt-0.5" style={{ color: '#666666' }}>
                {application.application_id} · {application.loan_type}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm">
            <StatusBadge status={application.status} />
            <span style={{ color: '#444444' }}>·</span>
            <span style={{ color: '#A0A0A0' }}>
              {completedDocs}/{application.documents.length} documents processed
            </span>
            <span style={{ color: '#444444' }}>·</span>
            <span style={{ color: '#666666' }}>
              Updated {formatDateTime(application.updated_at)}
            </span>
          </div>
        </div>

        {/* Right side: Risk */}
        <div className="flex items-center gap-6 md:text-right">
          <div>
            <p className="text-xs uppercase tracking-wider mb-1" style={{ color: '#555555' }}>
              Risk Score
            </p>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold tabular-nums" style={{ color: '#F0F0F0' }}>
                {application.risk.score}
              </span>
              <span className="text-xs" style={{ color: '#555555' }}>/100</span>
            </div>
          </div>
          <div className="w-px h-12" style={{ background: 'rgba(255,255,255,0.06)' }} />
          <div>
            <p className="text-xs uppercase tracking-wider mb-1.5" style={{ color: '#555555' }}>
              Risk Level
            </p>
            <RiskBadge level={application.risk.level} />
          </div>
        </div>
      </div>
    </div>
  );
}
