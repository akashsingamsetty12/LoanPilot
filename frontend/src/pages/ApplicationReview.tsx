import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Download
} from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { ApplicationHeader } from '../components/review/ApplicationHeader';
import { DocumentsSection } from '../components/review/DocumentsSection';
import { ExtractedFields } from '../components/review/ExtractedFields';
import { ComparisonTable } from '../components/review/ComparisonTable';
import { FlagsSection } from '../components/review/FlagsSection';
import { MissingDocuments } from '../components/review/MissingDocuments';
import { Recommendation } from '../components/review/Recommendation';
import { AskLoanIQ } from '../components/chat/AskLoanIQ';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { useApplication } from '../hooks/useApplication';

export function ApplicationReview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { application, loading, error, refetch } = useApplication(id);

  // Active section tab for review workspace navigation
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'extraction' | 'comparison' | 'flags'>('overview');

  // Action Modals
  const [modalAction, setModalAction] = useState<'approve' | 'reject' | 'request_info' | null>(null);
  const [actionReason, setActionReason] = useState('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const handleDecisionSubmit = () => {
    if (!modalAction) return;
    const actionText =
      modalAction === 'approve'
        ? 'Application Approved'
        : modalAction === 'reject'
        ? 'Application Rejected'
        : 'Additional Information Requested';

    setActionSuccess(`${actionText} successfully recorded.`);
    setModalAction(null);
    setActionReason('');
    refetch();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Topbar title="Application Review" subtitle="Loading application details..." />
        <div className="flex-1 flex items-center justify-center">
          <Spinner size="lg" text="Loading loan application review details..." />
        </div>
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="min-h-screen flex flex-col">
        <Topbar title="Application Review" subtitle="Error loading review workspace" />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          <ErrorState
            title="Failed to Load Application"
            message={error || 'The requested application could not be found.'}
            onRetry={refetch}
          />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col relative pb-16">
      <Topbar
        title={`Review — ${application.applicant_name}`}
        subtitle={`Application ID: ${application.application_id}`}
      />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {/* Navigation back and Action Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center text-xs font-medium text-charcoal-muted hover:text-charcoal transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
          </button>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              icon={Download}
              onClick={() => navigate(`/applications/${application.application_id}/report`)}
            >
              Generate Report
            </Button>
            <Button
              variant="outline"
              size="sm"
              icon={AlertCircle}
              onClick={() => setModalAction('request_info')}
            >
              Request Info
            </Button>
            <Button
              variant="danger"
              size="sm"
              icon={XCircle}
              onClick={() => setModalAction('reject')}
            >
              Reject
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={CheckCircle2}
              onClick={() => setModalAction('approve')}
            >
              Approve Application
            </Button>
          </div>
        </div>

        {/* Action Success Toast/Banner */}
        {actionSuccess && (
          <div className="p-4 bg-risk-low-light border border-risk-low/30 rounded-lg flex items-center justify-between text-xs font-medium text-risk-low">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              <span>{actionSuccess}</span>
            </div>
            <button onClick={() => setActionSuccess(null)} className="underline text-xs">
              Dismiss
            </button>
          </div>
        )}

        {/* Section A: Overview Header with Risk Score */}
        <ApplicationHeader application={application} />

        {/* Navigation Tabs */}
        <div className="border-b border-surface-300 flex items-center gap-4 overflow-x-auto">
          {[
            { id: 'overview', label: 'All Review Sections' },
            { id: 'documents', label: `Documents (${application.documents.length})` },
            { id: 'extraction', label: 'Extracted Fields & Evidence' },
            { id: 'comparison', label: 'Cross-Doc Verification' },
            { id: 'flags', label: `Risk Flags (${application.risk.flags.length})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`pb-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-brand-600 text-brand-600'
                  : 'border-transparent text-charcoal-muted hover:text-charcoal'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Review Sections */}
        {activeTab === 'overview' ? (
          <div className="space-y-6">
            {/* Section G: Final Recommendation */}
            <Recommendation recommendation={application.recommendation} />

            {/* Section F: Missing Documents warning if any */}
            {application.verification.missing_documents.length > 0 && (
              <MissingDocuments documents={application.verification.missing_documents} />
            )}

            {/* Section E: Risk Flags */}
            <FlagsSection flags={application.risk.flags} />

            {/* Section D: Cross-Document Comparison */}
            <ComparisonTable
              matches={application.verification.matches}
              mismatches={application.verification.mismatches}
            />

            {/* Section B: Document List & Confidence */}
            <DocumentsSection documents={application.documents} />

            {/* Section C: Extracted Fields & Evidence */}
            <ExtractedFields documents={application.documents} />
          </div>
        ) : activeTab === 'documents' ? (
          <DocumentsSection documents={application.documents} />
        ) : activeTab === 'extraction' ? (
          <ExtractedFields documents={application.documents} />
        ) : activeTab === 'comparison' ? (
          <ComparisonTable
            matches={application.verification.matches}
            mismatches={application.verification.mismatches}
          />
        ) : (
          <FlagsSection flags={application.risk.flags} />
        )}
      </main>

      {/* Floating Ask LoanIQ Chat Widget */}
      <AskLoanIQ applicationId={application.application_id} />

      {/* Action Modal */}
      <Modal
        isOpen={Boolean(modalAction)}
        onClose={() => setModalAction(null)}
        title={
          modalAction === 'approve'
            ? 'Approve Loan Application'
            : modalAction === 'reject'
            ? 'Reject Loan Application'
            : 'Request Additional Information'
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-charcoal-secondary">
            {modalAction === 'approve'
              ? 'Are you sure you want to approve this application? This action will mark the document verification complete.'
              : modalAction === 'reject'
              ? 'Please provide a clear reason for rejecting this application for audit compliance.'
              : 'Specify what additional documents or info are required from the borrower.'}
          </p>

          <div>
            <label className="block text-xs font-medium text-charcoal-muted mb-1">
              Officer Notes / Justification
            </label>
            <textarea
              rows={3}
              value={actionReason}
              onChange={(e) => setActionReason(e.target.value)}
              placeholder="Enter notes for audit trail..."
              className="input-field w-full text-sm"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2 border-t border-surface-200">
            <Button variant="outline" size="sm" onClick={() => setModalAction(null)}>
              Cancel
            </Button>
            <Button
              variant={modalAction === 'reject' ? 'danger' : 'primary'}
              size="sm"
              onClick={handleDecisionSubmit}
            >
              Confirm Decision
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
