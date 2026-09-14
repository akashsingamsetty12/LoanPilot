import { useNavigate } from 'react-router-dom';
import { Eye, ArrowUpRight } from 'lucide-react';
import type { Application } from '../../types';
import { StatusBadge, RiskBadge } from './StatusBadge';
import { formatDate } from '../../lib/utils';

interface ApplicationTableProps {
  applications: Application[];
}

export function ApplicationTable({ applications }: ApplicationTableProps) {
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            {[
              'Application ID',
              'Applicant',
              'Loan Type',
              'Documents',
              'Risk',
              'Status',
              'Updated',
              'Action',
            ].map((header, i) => (
              <th
                key={header}
                className={`py-3 px-4 text-xs font-semibold uppercase tracking-wider ${
                  i === 3 || i === 4 || i === 5 ? 'text-center' : i === 7 ? 'text-right' : 'text-left'
                }`}
                style={{ color: '#444444' }}
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {applications.map((app, idx) => {
            const completedDocs = app.documents.filter(
              (d) => d.status === 'completed'
            ).length;
            return (
              <tr
                key={app.application_id}
                className="group cursor-pointer transition-all duration-150"
                style={{
                  borderBottom: '1px solid rgba(255,255,255,0.04)',
                }}
                onClick={() => navigate(`/applications/${app.application_id}`)}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLTableRowElement).style.background =
                    'rgba(255,255,255,0.02)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLTableRowElement).style.background =
                    'transparent';
                }}
              >
                <td className="py-3.5 px-4">
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
                </td>
                <td className="py-3.5 px-4">
                  <div>
                    <p className="font-medium" style={{ color: '#F0F0F0' }}>
                      {app.applicant_name}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: '#444444' }}>
                      {app.applicant_email}
                    </p>
                  </div>
                </td>
                <td className="py-3.5 px-4">
                  <span style={{ color: '#A0A0A0' }}>{app.loan_type}</span>
                </td>
                <td className="py-3.5 px-4 text-center">
                  <span
                    className="font-mono text-xs tabular-nums px-2 py-0.5 rounded"
                    style={{
                      background: '#1A1A1A',
                      color: '#A0A0A0',
                      border: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    {completedDocs}/{app.documents.length}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-center">
                  <RiskBadge level={app.risk.level} />
                </td>
                <td className="py-3.5 px-4 text-center">
                  <StatusBadge status={app.status} />
                </td>
                <td className="py-3.5 px-4">
                  <span style={{ color: '#444444' }}>{formatDate(app.updated_at)}</span>
                </td>
                <td className="py-3.5 px-4 text-right">
                  <button
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-150 opacity-0 group-hover:opacity-100"
                    style={{
                      background: 'rgba(170,255,0,0.08)',
                      color: '#AAFF00',
                      border: '1px solid rgba(170,255,0,0.15)',
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/applications/${app.application_id}`);
                    }}
                    aria-label={`View application ${app.application_id}`}
                  >
                    <Eye className="h-3.5 w-3.5" />
                    View
                    <ArrowUpRight className="h-3 w-3" />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
