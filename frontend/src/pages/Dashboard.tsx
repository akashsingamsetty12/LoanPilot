import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Filter, RefreshCw } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { SummaryCards } from '../components/applications/SummaryCards';
import { ApplicationTable } from '../components/applications/ApplicationTable';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { useApplications } from '../hooks/useApplication';
import type { ApplicationStatus } from '../types';

export function Dashboard() {
  const navigate = useNavigate();
  const { applications, loading, error, refetch } = useApplications();
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | 'ALL'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredApplications = useMemo(() => {
    return applications.filter((app) => {
      const matchesStatus = statusFilter === 'ALL' || app.status === statusFilter;
      const matchesSearch =
        app.applicant_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.application_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.loan_type.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [applications, statusFilter, searchQuery]);

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar
        title="Dashboard"
        subtitle="LoanIQ AI Document Processing & Verification Agent"
      />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {/* Top actions & summary */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-charcoal">Applications Overview</h2>
            <p className="text-sm text-charcoal-muted">
              Monitor, review, and make human decisions on processed loan applications.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              icon={RefreshCw}
              onClick={refetch}
              disabled={loading}
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Plus}
              onClick={() => navigate('/applications/new')}
            >
              New Application
            </Button>
          </div>
        </div>

        {/* Summary Metrics Cards */}
        <SummaryCards applications={applications} />

        {/* Filters and Table Controls */}
        <div className="bg-white p-4 rounded-lg border border-surface-300 shadow-sm space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Status Tabs */}
            <div className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0">
              <span className="text-xs font-semibold text-charcoal-muted uppercase mr-2 flex items-center gap-1">
                <Filter className="h-3.5 w-3.5" /> Filter:
              </span>
              {(['ALL', 'review', 'processing', 'completed', 'rejected'] as const).map(
                (status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status as any)}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors capitalize whitespace-nowrap ${
                      statusFilter === status
                        ? 'bg-brand-600 text-white shadow-xs'
                        : 'bg-surface-100 text-charcoal-muted hover:bg-surface-200 hover:text-charcoal'
                    }`}
                  >
                    {status === 'ALL'
                      ? `All (${applications.length})`
                      : status === 'review'
                      ? `Under Review (${applications.filter((a) => a.status === 'review').length})`
                      : status === 'processing'
                      ? `Processing (${applications.filter((a) => a.status === 'processing').length})`
                      : status === 'completed'
                      ? `Completed (${applications.filter((a) => a.status === 'completed').length})`
                      : `Rejected (${applications.filter((a) => a.status === 'rejected').length})`}
                  </button>
                )
              )}
            </div>

            {/* Search Input */}
            <div className="w-full md:w-64">
              <input
                type="text"
                placeholder="Search applicant or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field w-full text-xs"
              />
            </div>
          </div>

          {/* Table / Content States */}
          {loading ? (
            <div className="py-12 flex justify-center">
              <Spinner size="lg" text="Loading loan applications..." />
            </div>
          ) : error ? (
            <ErrorState
              title="Failed to load applications"
              message={error}
              onRetry={refetch}
            />
          ) : filteredApplications.length === 0 ? (
            <EmptyState
              title="No applications found"
              message={
                searchQuery || statusFilter !== 'ALL'
                  ? 'No applications match your selected filter criteria.'
                  : 'Start by uploading documents to create your first loan application.'
              }
              actionLabel={searchQuery || statusFilter !== 'ALL' ? undefined : 'Create New Application'}
              onAction={searchQuery || statusFilter !== 'ALL' ? undefined : () => navigate('/applications/new')}
            />
          ) : (
            <ApplicationTable applications={filteredApplications} />
          )}
        </div>
      </main>
    </div>
  );
}
