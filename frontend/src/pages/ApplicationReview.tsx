import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Download,
  ExternalLink,
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
import { decideApplication } from '../api/applications';
import type { LoanDocument } from '../types';

export function ApplicationReview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { application, loading, error, refetch } = useApplication(id);

  // Active section tab for review workspace navigation
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'extraction' | 'comparison' | 'flags'>('overview');

  // Document preview modal state
  const [viewingDoc, setViewingDoc] = useState<LoanDocument | null>(null);

  // Action Modals
  const [modalAction, setModalAction] = useState<'approve' | 'reject' | 'request_info' | null>(null);
  const [actionReason, setActionReason] = useState('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [submittingDecision, setSubmittingDecision] = useState(false);

  const handleViewDocument = (docId: string) => {
    const doc = application?.documents?.find((d) => d.document_id === docId);
    if (doc) {
      setViewingDoc(doc);
    } else {
      const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/documents/${docId}/file`;
      window.open(url, '_blank');
    }
  };

  const handleDecisionSubmit = async () => {
    if (!modalAction || !application) return;
    const decisionValue =
      modalAction === 'approve'
        ? 'approved'
        : modalAction === 'reject'
          ? 'rejected'
          : 'needs_more_info';

    setSubmittingDecision(true);
    try {
      await decideApplication(application.application_id, {
        decision: decisionValue,
        notes: actionReason.trim() || undefined,
        decided_by: 'Loan Officer',
      });

      const actionText =
        modalAction === 'approve'
          ? 'Application Approved'
          : modalAction === 'reject'
            ? 'Application Rejected'
            : 'Additional Information Requested';

      setActionSuccess(`${actionText} successfully recorded.`);
      setModalAction(null);
      setActionReason('');
      await refetch();
    } catch (err: any) {
      alert(err.message || 'Failed to submit decision.');
    } finally {
      setSubmittingDecision(false);
    }
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
          <div
            className="p-4 rounded-xl flex items-center justify-between text-xs font-medium"
            style={{
              background: 'rgba(48,209,88,0.1)',
              border: '1px solid rgba(48,209,88,0.25)',
              color: '#30D158',
            }}
          >
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              <span>{actionSuccess}</span>
            </div>
            <button onClick={() => setActionSuccess(null)} className="underline text-xs opacity-80 hover:opacity-100">
              Dismiss
            </button>
          </div>
        )}

        {/* Section A: Overview Header with Risk Score */}
        <ApplicationHeader application={application} />

        {/* Navigation Tabs */}
        <div className="flex items-center gap-6 overflow-x-auto" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
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
              className="pb-3 text-sm font-medium transition-all duration-150 border-b-2 whitespace-nowrap"
              style={
                activeTab === tab.id
                  ? {
                      borderColor: '#AAFF00',
                      color: '#AAFF00',
                    }
                  : {
                      borderColor: 'transparent',
                      color: '#666666',
                    }
              }
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
            <DocumentsSection documents={application.documents} onViewDocument={handleViewDocument} />

            {/* Section C: Extracted Fields & Evidence */}
            <ExtractedFields documents={application.documents} />
          </div>
        ) : activeTab === 'documents' ? (
          <DocumentsSection documents={application.documents} onViewDocument={handleViewDocument} />
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
        onClose={() => !submittingDecision && setModalAction(null)}
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
              disabled={submittingDecision}
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-white/[0.06]">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setModalAction(null)}
              disabled={submittingDecision}
            >
              Cancel
            </Button>
            <Button
              variant={modalAction === 'reject' ? 'danger' : 'primary'}
              size="sm"
              onClick={handleDecisionSubmit}
              loading={submittingDecision}
            >
              Confirm Decision
            </Button>
          </div>
        </div>
      </Modal>

      {/* Document Preview Modal */}
      <Modal
        isOpen={Boolean(viewingDoc)}
        onClose={() => setViewingDoc(null)}
        title={viewingDoc ? `Document Preview — ${viewingDoc.file_name}` : 'Document Preview'}
        size="xl"
      >
        {viewingDoc && (
          <div className="space-y-4">
            <div
              className="flex flex-wrap items-center justify-between gap-2 p-3.5 rounded-xl text-xs"
              style={{
                background: '#181818',
                border: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <div className="flex items-center gap-4">
                <div>
                  <span style={{ color: '#666666' }}>Type: </span>
                  <span className="font-semibold capitalize" style={{ color: '#F0F0F0' }}>
                    {viewingDoc.type ? viewingDoc.type.replace(/_/g, ' ') : 'Unknown'}
                  </span>
                </div>
                <div>
                  <span style={{ color: '#666666' }}>Pages: </span>
                  <span className="font-semibold" style={{ color: '#F0F0F0' }}>{viewingDoc.pages || 1}</span>
                </div>
                <div>
                  <span style={{ color: '#666666' }}>OCR Confidence: </span>
                  <span className="font-semibold" style={{ color: '#F0F0F0' }}>{viewingDoc.ocr_confidence}%</span>
                </div>
              </div>
              <a
                href={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/documents/${viewingDoc.document_id}/file`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 font-medium hover:underline"
                style={{ color: '#AAFF00' }}
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Open Raw File in New Tab
              </a>
            </div>

            {/* In-Browser Document Viewer */}
            <div
              className="h-96 w-full rounded-xl overflow-hidden flex items-center justify-center p-2"
              style={{
                background: '#0A0A0A',
                border: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              {viewingDoc.file_name.match(/\.(jpeg|jpg|png|webp|gif)$/i) ? (
                <img
                  src={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/documents/${viewingDoc.document_id}/file`}
                  alt={viewingDoc.file_name}
                  className="max-h-full max-w-full object-contain rounded"
                />
              ) : (
                <iframe
                  src={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/documents/${viewingDoc.document_id}/file`}
                  title={viewingDoc.file_name}
                  className="w-full h-full border-0 rounded"
                />
              )}
            </div>

            {/* Extracted Fields Table */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: '#555555' }}>
                Extracted Fields ({viewingDoc.fields?.length || 0})
              </h4>
              {viewingDoc.fields && viewingDoc.fields.length > 0 ? (
                <div
                  className="max-h-48 overflow-y-auto rounded-xl divide-y"
                  style={{
                    background: '#161616',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderColor: 'rgba(255,255,255,0.04)',
                  }}
                >
                  {viewingDoc.fields.map((f, idx) => (
                    <div key={idx} className="p-3 flex items-center justify-between text-xs">
                      <span className="font-medium" style={{ color: '#888888' }}>{f.field_name}</span>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold" style={{ color: '#F0F0F0' }}>{f.value}</span>
                        <span className="text-[10px]" style={{ color: '#555555' }}>({f.confidence}%)</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p
                  className="text-xs italic p-3 rounded-lg"
                  style={{
                    background: '#161616',
                    border: '1px solid rgba(255,255,255,0.06)',
                    color: '#666666',
                  }}
                >
                  No structured fields extracted from this document yet.
                </p>
              )}
            </div>

            <div className="flex justify-end pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <Button variant="outline" size="sm" onClick={() => setViewingDoc(null)}>
                Close Preview
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
