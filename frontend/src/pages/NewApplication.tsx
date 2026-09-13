import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilePlus, ArrowLeft, Check, AlertCircle } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { DocumentUpload } from '../components/documents/DocumentUpload';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { createApplication } from '../api/applications';
import { useUpload } from '../hooks/useUpload';
import type { LoanType } from '../types';

export function NewApplication() {
  const navigate = useNavigate();

  // Form State
  const [applicantName, setApplicantName] = useState('');
  const [applicantEmail, setApplicantEmail] = useState('');
  const [requestedAmount, setRequestedAmount] = useState('');
  const [loanType, setLoanType] = useState<LoanType>('PERSONAL_LOAN');

  // Application Creation State
  const [createdAppId, setCreatedAppId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Upload Hook (initialized once applicationId is created, or dummy temp ID)
  const { files, uploading, error: uploadError, addFiles, removeFile, upload } = useUpload(
    createdAppId || 'TEMP'
  );

  const handleCreateApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!applicantName.trim()) {
      setFormError('Applicant name is required.');
      return;
    }
    const amountNum = parseFloat(requestedAmount);
    if (!requestedAmount || isNaN(amountNum) || amountNum <= 0) {
      setFormError('Please enter a valid requested loan amount.');
      return;
    }

    setCreating(true);
    setFormError(null);

    try {
      const newApp = await createApplication({
        applicant_name: applicantName.trim(),
        applicant_email: applicantEmail.trim() || 'applicant@example.com',
        loan_type: loanType,
      });

      setCreatedAppId(newApp.application_id);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to create application.');
    } finally {
      setCreating(false);
    }
  };

  const handleUploadAndProceed = async () => {
    if (files.length > 0 && createdAppId) {
      await upload();
      // Navigate to review page
      navigate(`/applications/${createdAppId}`);
    } else if (createdAppId) {
      navigate(`/applications/${createdAppId}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar
        title="New Loan Application"
        subtitle="Initiate loan processing and upload borrower documentation"
      />

      <main className="flex-1 p-6 max-w-4xl w-full mx-auto space-y-6">
        {/* Navigation back */}
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center text-xs font-medium text-charcoal-muted hover:text-charcoal transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
        </button>

        {/* Step 1: Applicant Details */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-surface-200">
            <div className="w-8 h-8 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm">
              1
            </div>
            <div>
              <h2 className="text-lg font-semibold text-charcoal">Applicant Information</h2>
              <p className="text-xs text-charcoal-muted">
                Enter primary details for the loan applicant
              </p>
            </div>
          </div>

          <form onSubmit={handleCreateApplication} className="space-y-4">
            {formError && (
              <div className="p-3 bg-risk-high-light border border-risk-high/20 rounded-md flex items-center gap-2 text-xs text-risk-high">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-charcoal-secondary mb-1">
                  Full Name <span className="text-risk-high">*</span>
                </label>
                <input
                  type="text"
                  required
                  disabled={Boolean(createdAppId)}
                  value={applicantName}
                  onChange={(e) => setApplicantName(e.target.value)}
                  placeholder="e.g. Ramesh Kumar"
                  className="input-field w-full text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-charcoal-secondary mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  disabled={Boolean(createdAppId)}
                  value={applicantEmail}
                  onChange={(e) => setApplicantEmail(e.target.value)}
                  placeholder="e.g. ramesh.kumar@example.com"
                  className="input-field w-full text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-charcoal-secondary mb-1">
                  Requested Loan Amount (₹) <span className="text-risk-high">*</span>
                </label>
                <input
                  type="number"
                  required
                  disabled={Boolean(createdAppId)}
                  value={requestedAmount}
                  onChange={(e) => setRequestedAmount(e.target.value)}
                  placeholder="e.g. 500000"
                  className="input-field w-full text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-charcoal-secondary mb-1">
                  Loan Product Type <span className="text-risk-high">*</span>
                </label>
                <select
                  disabled={Boolean(createdAppId)}
                  value={loanType}
                  onChange={(e) => setLoanType(e.target.value as LoanType)}
                  className="input-field w-full text-sm"
                >
                  <option value="PERSONAL_LOAN">Personal Loan</option>
                  <option value="HOME_LOAN">Home Loan / Mortgage</option>
                  <option value="AUTO_LOAN">Auto Loan</option>
                  <option value="BUSINESS_LOAN">Business Loan</option>
                </select>
              </div>
            </div>

            {!createdAppId && (
              <div className="pt-2 flex justify-end">
                <Button type="submit" loading={creating} icon={FilePlus}>
                  Initialize Application
                </Button>
              </div>
            )}
          </form>
        </Card>

        {/* Step 2: Document Upload */}
        <Card className={`p-6 ${!createdAppId ? 'opacity-50 pointer-events-none' : ''}`}>
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-surface-200">
            <div className="w-8 h-8 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-sm">
              2
            </div>
            <div>
              <h2 className="text-lg font-semibold text-charcoal">Upload Loan Documents</h2>
              <p className="text-xs text-charcoal-muted">
                Upload Identity proofs, Bank Statements, Salary Slips, or Tax Returns (ITR)
              </p>
            </div>
          </div>

          {uploadError && (
            <div className="mb-4 p-3 bg-risk-high-light border border-risk-high/20 rounded-md flex items-center gap-2 text-xs text-risk-high">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <DocumentUpload
            files={files}
            uploading={uploading}
            onAddFiles={addFiles}
            onRemoveFile={removeFile}
            onUpload={upload}
          />

          {createdAppId && (
            <div className="mt-6 pt-4 border-t border-surface-200 flex justify-between items-center">
              <span className="text-xs text-charcoal-muted">
                App ID: <span className="font-mono font-medium text-charcoal">{createdAppId}</span>
              </span>
              <Button
                variant="primary"
                onClick={handleUploadAndProceed}
                loading={uploading}
                icon={Check}
              >
                Proceed to Application Review
              </Button>
            </div>
          )}
        </Card>
      </main>
    </div>
  );
}
