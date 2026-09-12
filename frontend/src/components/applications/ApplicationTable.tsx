import { useNavigate } from 'react-router-dom';
import { Eye } from 'lucide-react';
import type { Application } from '../../types';
import { StatusBadge, RiskBadge } from './StatusBadge';
import { formatDate } from '../../lib/utils';
import { Button } from '../ui/Button';

interface ApplicationTableProps {
  applications: Application[];
}

export function ApplicationTable({ applications }: ApplicationTableProps) {
  const navigate = useNavigate();

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-300">
            <th className="text-left py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Application ID</th>
            <th className="text-left py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Applicant</th>
            <th className="text-left py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Loan Type</th>
            <th className="text-center py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Documents</th>
            <th className="text-center py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Risk</th>
            <th className="text-center py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Status</th>
            <th className="text-left py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Updated</th>
            <th className="text-right py-3 px-4 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Action</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => {
            const completedDocs = app.documents.filter(d => d.status === 'completed').length;
            return (
              <tr
                key={app.application_id}
                className="border-b border-surface-200 hover:bg-surface-50 transition-colors cursor-pointer"
                onClick={() => navigate(`/applications/${app.application_id}`)}
              >
                <td className="py-3 px-4 font-medium text-charcoal">{app.application_id}</td>
                <td className="py-3 px-4">
                  <div>
                    <p className="font-medium text-charcoal">{app.applicant_name}</p>
                    <p className="text-xs text-charcoal-muted">{app.applicant_email}</p>
                  </div>
                </td>
                <td className="py-3 px-4 text-charcoal-secondary">{app.loan_type}</td>
                <td className="py-3 px-4 text-center">
                  <span className="text-charcoal tabular-nums">{completedDocs}/{app.documents.length}</span>
                </td>
                <td className="py-3 px-4 text-center">
                  <RiskBadge level={app.risk.level} />
                </td>
                <td className="py-3 px-4 text-center">
                  <StatusBadge status={app.status} />
                </td>
                <td className="py-3 px-4 text-charcoal-muted">{formatDate(app.updated_at)}</td>
                <td className="py-3 px-4 text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/applications/${app.application_id}`);
                    }}
                    aria-label={`View application ${app.application_id}`}
                  >
                    <Eye className="h-4 w-4" />
                    View
                  </Button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
