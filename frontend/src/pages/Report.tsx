import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { ReportViewer } from '../components/reports/ReportViewer';

export function Report() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar
        title="Verification Report"
        subtitle={`Audit-ready summary for Application ID: ${id || 'N/A'}`}
      />

      <main className="flex-1 p-6 max-w-5xl w-full mx-auto space-y-6">
        <button
          onClick={() => navigate(id ? `/applications/${id}` : '/')}
          className="inline-flex items-center text-xs font-medium text-charcoal-muted hover:text-charcoal transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Review Workspace
        </button>

        {id ? (
          <ReportViewer applicationId={id} />
        ) : (
          <div className="bg-white p-8 rounded-lg border border-surface-300 text-center text-charcoal-muted text-sm">
            No Application ID specified.
          </div>
        )}
      </main>
    </div>
  );
}
