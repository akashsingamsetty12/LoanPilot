import { useNavigate } from 'react-router-dom';
import { FileText, ArrowUpRight, BarChart3, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { useApplications } from '../hooks/useApplication';
import { formatDate } from '../lib/utils';
import { RiskBadge } from '../components/applications/StatusBadge';

export function Reports() {
  const navigate = useNavigate();
  const { applications, loading, error, refetch } = useApplications();

  // Only show applications that have been through processing (have something to report on)
  const reportableApps = applications.filter(
    (a) => a.status === 'review' || a.status === 'completed' || a.status === 'rejected'
  );

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#0A0A0A' }}>
      <Topbar
        title="Reports"
        subtitle="Audit-ready verification reports for processed applications"
      />

      <main className="flex-1 p-6 max-w-5xl w-full mx-auto space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 flex-shrink-0" style={{ color: '#AAFF00' }} />
          <div>
            <h2 className="text-xl font-bold" style={{ color: '#F0F0F0' }}>
              Verification Reports
            </h2>
            <p className="text-sm" style={{ color: '#444444' }}>
              Click any application below to view its full verification report.
            </p>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="py-20 flex justify-center">
            <Spinner size="lg" text="Loading reports..." />
          </div>
        ) : error ? (
          <ErrorState title="Failed to load reports" message={error} onRetry={refetch} />
        ) : reportableApps.length === 0 ? (
          <div
            className="rounded-xl p-12 flex flex-col items-center justify-center text-center"
            style={{ background: '#111111', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
              style={{ background: 'rgba(170,255,0,0.08)', border: '1px solid rgba(170,255,0,0.12)' }}
            >
              <FileText className="h-6 w-6" style={{ color: '#AAFF00' }} />
            </div>
            <p className="text-base font-medium mb-1" style={{ color: '#F0F0F0' }}>
              No reports available yet
            </p>
            <p className="text-sm" style={{ color: '#444444' }}>
              Reports are generated once applications complete AI processing and are under review.
            </p>
          </div>
        ) : (
          <div
            className="rounded-xl overflow-hidden"
            style={{ background: '#111111', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            {/* Table header */}
            <div
              className="grid grid-cols-[1fr_1fr_120px_120px_120px] gap-4 px-5 py-3 text-xs font-semibold uppercase tracking-wider"
              style={{
                color: '#444444',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <span>Application</span>
              <span>Applicant</span>
              <span className="text-center">Risk</span>
              <span className="text-center">Status</span>
              <span className="text-right">Report</span>
            </div>

            {/* Rows */}
            {reportableApps.map((app) => {
              const statusIcon =
                app.status === 'completed' ? (
                  <CheckCircle className="h-3.5 w-3.5" style={{ color: '#30D158' }} />
                ) : app.status === 'rejected' ? (
                  <AlertTriangle className="h-3.5 w-3.5" style={{ color: '#FF453A' }} />
                ) : (
                  <Clock className="h-3.5 w-3.5" style={{ color: '#FFB340' }} />
                );

              const statusColor =
                app.status === 'completed'
                  ? '#30D158'
                  : app.status === 'rejected'
                  ? '#FF453A'
                  : '#FFB340';

              return (
                <div
                  key={app.application_id}
                  className="group grid grid-cols-[1fr_1fr_120px_120px_120px] gap-4 px-5 py-4 items-center cursor-pointer transition-all duration-150"
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                  onClick={() => navigate(`/applications/${app.application_id}/report`)}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.02)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLDivElement).style.background = 'transparent';
                  }}
                >
                  {/* App ID + date */}
                  <div>
                    <span
                      className="font-mono text-xs font-medium px-2 py-0.5 rounded"
                      style={{
                        background: 'rgba(170,255,0,0.08)',
                        color: '#AAFF00',
                        border: '1px solid rgba(170,255,0,0.12)',
                      }}
                    >
                      {app.application_id}
                    </span>
                    <p className="text-xs mt-1.5" style={{ color: '#444444' }}>
                      {formatDate(app.updated_at)}
                    </p>
                  </div>

                  {/* Applicant */}
                  <div>
                    <p className="text-sm font-medium" style={{ color: '#F0F0F0' }}>
                      {app.applicant_name}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: '#444444' }}>
                      {app.loan_type}
                    </p>
                  </div>

                  {/* Risk */}
                  <div className="flex justify-center">
                    <RiskBadge level={app.risk.level} />
                  </div>

                  {/* Status */}
                  <div className="flex items-center justify-center gap-1.5">
                    {statusIcon}
                    <span className="text-xs font-medium capitalize" style={{ color: statusColor }}>
                      {app.status}
                    </span>
                  </div>

                  {/* View report button */}
                  <div className="flex justify-end">
                    <button
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-150 opacity-0 group-hover:opacity-100"
                      style={{
                        background: 'rgba(170,255,0,0.08)',
                        color: '#AAFF00',
                        border: '1px solid rgba(170,255,0,0.15)',
                      }}
                    >
                      View
                      <ArrowUpRight className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
