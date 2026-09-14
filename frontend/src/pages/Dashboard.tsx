import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Filter, RefreshCw, TrendingUp } from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { SummaryCards } from '../components/applications/SummaryCards';
import { ApplicationTable } from '../components/applications/ApplicationTable';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { useApplications } from '../hooks/useApplication';
import type { ApplicationStatus } from '../types';

const STATUS_TABS = ['ALL', 'review', 'processing', 'completed', 'rejected'] as const;

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

  const getTabLabel = (status: (typeof STATUS_TABS)[number]) => {
    if (status === 'ALL') return `All (${applications.length})`;
    const count = applications.filter((a) => a.status === status).length;
    const labels: Record<string, string> = {
      review: 'Under Review',
      processing: 'Processing',
      completed: 'Completed',
      rejected: 'Rejected',
    };
    return `${labels[status]} (${count})`;
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#0A0A0A' }}>
      <Topbar
        title="Dashboard"
        subtitle="LoanPilot AI Document Processing & Verification Agent"
      />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6 animate-fade-in">
        {/* Header row */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4" style={{ color: '#AAFF00' }} />
              <h2 className="text-xl font-bold" style={{ color: '#F0F0F0' }}>
                Applications Overview
              </h2>
            </div>
            <p className="text-sm" style={{ color: '#444444' }}>
              Monitor, review, and make decisions on processed loan applications.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
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

        {/* Summary Metric Cards */}
        <SummaryCards applications={applications} />

        {/* Filters & Table */}
        <div
          className="rounded-xl overflow-hidden"
          style={{
            background: '#111111',
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          {/* Filter bar */}
          <div
            className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4"
            style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
          >
            {/* Status Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5">
              <span
                className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 mr-1 flex-shrink-0"
                style={{ color: '#444444' }}
              >
                <Filter className="h-3 w-3" />
                Filter
              </span>
              {STATUS_TABS.map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status as any)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 whitespace-nowrap capitalize"
                  style={
                    statusFilter === status
                      ? {
                          background: 'rgba(170,255,0,0.12)',
                          color: '#AAFF00',
                          border: '1px solid rgba(170,255,0,0.2)',
                        }
                      : {
                          background: '#1A1A1A',
                          color: '#555555',
                          border: '1px solid rgba(255,255,255,0.06)',
                        }
                  }
                >
                  {getTabLabel(status)}
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="w-full md:w-60 flex-shrink-0">
              <input
                type="text"
                placeholder="Search applicant or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field w-full text-xs"
                aria-label="Search applications"
              />
            </div>
          </div>

          {/* Table / Content States */}
          <div className="p-1">
            {loading ? (
              <div className="py-16 flex justify-center">
                <Spinner size="lg" text="Loading loan applications..." />
              </div>
            ) : error ? (
              <div className="p-4">
                <ErrorState
                  title="Failed to load applications"
                  message={error}
                  onRetry={refetch}
                />
              </div>
            ) : filteredApplications.length === 0 ? (
              <div className="p-4">
                <EmptyState
                  title="No applications found"
                  message={
                    searchQuery || statusFilter !== 'ALL'
                      ? 'No applications match your selected filter criteria.'
                      : 'Start by uploading documents to create your first loan application.'
                  }
                  actionLabel={
                    searchQuery || statusFilter !== 'ALL'
                      ? undefined
                      : 'Create New Application'
                  }
                  onAction={
                    searchQuery || statusFilter !== 'ALL'
                      ? undefined
                      : () => navigate('/applications/new')
                  }
                />
              </div>
            ) : (
              <ApplicationTable applications={filteredApplications} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
