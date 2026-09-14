import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  ArrowUpRight,
  BarChart3,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert,
  ShieldCheck,
  Search,
  RefreshCw,
  TrendingUp,
} from 'lucide-react';
import { Topbar } from '../components/layout/Topbar';
import { Spinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { Button } from '../components/ui/Button';
import { useApplications } from '../hooks/useApplication';
import { formatDate } from '../lib/utils';
import { RiskBadge, StatusBadge } from '../components/applications/StatusBadge';
import type { RiskLevel } from '../types';

type FilterType = 'ALL' | 'completed' | 'review' | 'rejected' | 'HIGH' | 'MEDIUM' | 'LOW_PASS';

export function Reports() {
  const navigate = useNavigate();
  const { applications, loading, error, refetch } = useApplications();
  const [activeFilter, setActiveFilter] = useState<FilterType>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Applications that have undergone AI evaluation / processing
  const reportableApps = useMemo(() => {
    return applications.filter(
      (a) => a.status === 'review' || a.status === 'completed' || a.status === 'rejected'
    );
  }, [applications]);

  // Executive Stats Computations
  const stats = useMemo(() => {
    const totalEvaluated = reportableApps.length;
    const approved = reportableApps.filter((a) => a.status === 'completed').length;
    const rejected = reportableApps.filter((a) => a.status === 'rejected').length;
    const underReview = reportableApps.filter((a) => a.status === 'review').length;
    const decided = approved + rejected;

    const approvalRate = decided > 0 ? Math.round((approved / decided) * 100) : 0;
    const rejectionRate = decided > 0 ? Math.round((rejected / decided) * 100) : 0;

    // Risk Classifications
    const highRisk = reportableApps.filter((a) => a.risk?.level === 'HIGH').length;
    const mediumRisk = reportableApps.filter((a) => a.risk?.level === 'MEDIUM').length;
    const lowRisk = reportableApps.filter((a) => a.risk?.level === 'LOW').length;
    const passRisk = reportableApps.filter((a) => a.risk?.level === 'PASS').length;
    const lowPassCombined = lowRisk + passRisk;

    const highPct = totalEvaluated > 0 ? Math.round((highRisk / totalEvaluated) * 100) : 0;
    const medPct = totalEvaluated > 0 ? Math.round((mediumRisk / totalEvaluated) * 100) : 0;
    const lowPassPct = totalEvaluated > 0 ? Math.max(0, 100 - highPct - medPct) : 0;

    const avgRiskScore =
      totalEvaluated > 0
        ? Math.round(
            reportableApps.reduce((sum, a) => sum + (a.risk?.score || 0), 0) / totalEvaluated
          )
        : 0;

    return {
      totalEvaluated,
      approved,
      rejected,
      underReview,
      decided,
      approvalRate,
      rejectionRate,
      highRisk,
      mediumRisk,
      lowRisk,
      passRisk,
      lowPassCombined,
      highPct,
      medPct,
      lowPassPct,
      avgRiskScore,
    };
  }, [reportableApps]);

  // Filtered applications list
  const filteredApps = useMemo(() => {
    return reportableApps.filter((app) => {
      // Filter tab check
      let matchesFilter = true;
      if (activeFilter === 'completed') matchesFilter = app.status === 'completed';
      else if (activeFilter === 'rejected') matchesFilter = app.status === 'rejected';
      else if (activeFilter === 'review') matchesFilter = app.status === 'review';
      else if (activeFilter === 'HIGH') matchesFilter = app.risk?.level === 'HIGH';
      else if (activeFilter === 'MEDIUM') matchesFilter = app.risk?.level === 'MEDIUM';
      else if (activeFilter === 'LOW_PASS')
        matchesFilter = app.risk?.level === 'LOW' || app.risk?.level === 'PASS';

      // Search query check
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        app.applicant_name.toLowerCase().includes(q) ||
        app.application_id.toLowerCase().includes(q) ||
        app.loan_type.toLowerCase().includes(q);

      return matchesFilter && matchesSearch;
    });
  }, [reportableApps, activeFilter, searchQuery]);

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#0A0A0A' }}>
      <Topbar
        title="Reports & Analytics"
        subtitle="Executive underwriting metrics, risk distribution, and audit-ready verification dossiers"
      />

      <main className="flex-1 p-6 max-w-6xl w-full mx-auto space-y-6 animate-fade-in">
        {/* Header with Title & Refresh */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{
                background: 'rgba(170,255,0,0.08)',
                border: '1px solid rgba(170,255,0,0.2)',
              }}
            >
              <BarChart3 className="h-5 w-5" style={{ color: '#AAFF00' }} />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight" style={{ color: '#F0F0F0' }}>
                Underwriting & Risk Intelligence
              </h2>
              <p className="text-xs sm:text-sm" style={{ color: '#555555' }}>
                Statistical performance across loan approvals, rejections, and risk classifications.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <Button
              variant="secondary"
              size="sm"
              icon={RefreshCw}
              onClick={refetch}
              disabled={loading}
            >
              Refresh Stats
            </Button>
          </div>
        </div>

        {/* Executive KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Total Evaluated */}
          <div
            className="rounded-xl p-5 relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5"
            style={{
              background: '#111111',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#555555' }}>
                  Total Evaluated
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold tabular-nums" style={{ color: '#F0F0F0' }}>
                    {stats.totalEvaluated}
                  </span>
                  <span className="text-xs" style={{ color: '#666666' }}>
                    of {applications.length} apps
                  </span>
                </div>
              </div>
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ background: 'rgba(170,255,0,0.08)', border: '1px solid rgba(170,255,0,0.18)' }}
              >
                <FileText className="h-5 w-5" style={{ color: '#AAFF00' }} />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/[0.04] flex items-center justify-between text-xs">
              <span style={{ color: '#666666' }}>Pipeline conversion</span>
              <span className="font-medium" style={{ color: '#AAFF00' }}>
                {applications.length > 0 ? Math.round((stats.totalEvaluated / applications.length) * 100) : 0}% processed
              </span>
            </div>
          </div>

          {/* Card 2: Loan Approvals */}
          <div
            className="rounded-xl p-5 relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5"
            style={{
              background: '#111111',
              border: '1px solid rgba(48,209,88,0.18)',
            }}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#30D158' }}>
                  Loan Approvals
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold tabular-nums" style={{ color: '#30D158' }}>
                    {stats.approved}
                  </span>
                  <span
                    className="text-xs px-2 py-0.5 rounded font-medium"
                    style={{ background: 'rgba(48,209,88,0.12)', color: '#30D158' }}
                  >
                    {stats.approvalRate}% rate
                  </span>
                </div>
              </div>
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ background: 'rgba(48,209,88,0.1)', border: '1px solid rgba(48,209,88,0.2)' }}
              >
                <CheckCircle2 className="h-5 w-5" style={{ color: '#30D158' }} />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/[0.04] flex items-center justify-between text-xs">
              <span style={{ color: '#666666' }}>Decision outcome</span>
              <span className="font-medium" style={{ color: '#30D158' }}>
                {stats.approved} of {stats.decided} decided loans
              </span>
            </div>
          </div>

          {/* Card 3: Loan Rejections */}
          <div
            className="rounded-xl p-5 relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5"
            style={{
              background: '#111111',
              border: '1px solid rgba(255,69,58,0.18)',
            }}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#FF453A' }}>
                  Loan Rejections
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold tabular-nums" style={{ color: '#FF453A' }}>
                    {stats.rejected}
                  </span>
                  <span
                    className="text-xs px-2 py-0.5 rounded font-medium"
                    style={{ background: 'rgba(255,69,58,0.12)', color: '#FF453A' }}
                  >
                    {stats.rejectionRate}% rate
                  </span>
                </div>
              </div>
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ background: 'rgba(255,69,58,0.1)', border: '1px solid rgba(255,69,58,0.2)' }}
              >
                <XCircle className="h-5 w-5" style={{ color: '#FF453A' }} />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/[0.04] flex items-center justify-between text-xs">
              <span style={{ color: '#666666' }}>Risk threshold failed</span>
              <span className="font-medium" style={{ color: '#FF453A' }}>
                {stats.rejected} high variance cases
              </span>
            </div>
          </div>

          {/* Card 4: Under Review */}
          <div
            className="rounded-xl p-5 relative overflow-hidden transition-all duration-200 hover:-translate-y-0.5"
            style={{
              background: '#111111',
              border: '1px solid rgba(255,179,64,0.18)',
            }}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#FFB340' }}>
                  Under Officer Review
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold tabular-nums" style={{ color: '#FFB340' }}>
                    {stats.underReview}
                  </span>
                  <span
                    className="text-xs px-2 py-0.5 rounded font-medium"
                    style={{ background: 'rgba(255,179,64,0.12)', color: '#FFB340' }}
                  >
                    Pending action
                  </span>
                </div>
              </div>
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ background: 'rgba(255,179,64,0.1)', border: '1px solid rgba(255,179,64,0.2)' }}
              >
                <Clock className="h-5 w-5" style={{ color: '#FFB340' }} />
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/[0.04] flex items-center justify-between text-xs">
              <span style={{ color: '#666666' }}>Officer intervention</span>
              <span className="font-medium" style={{ color: '#FFB340' }}>
                Manual sign-off needed
              </span>
            </div>
          </div>
        </div>

        {/* Risk Classification Deep-Dive Panel */}
        <div
          className="rounded-xl p-6"
          style={{
            background: '#111111',
            border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          {/* Section header & Average Risk Index */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-5 border-b border-white/[0.06]">
            <div>
              <div className="flex items-center gap-2">
                <ShieldAlert className="h-4 w-4" style={{ color: '#AAFF00' }} />
                <h3 className="text-base font-bold" style={{ color: '#F0F0F0' }}>
                  Risk Classification Distribution
                </h3>
              </div>
              <p className="text-xs mt-1" style={{ color: '#555555' }}>
                Portfolio risk tiers evaluated across automated OCR, cross-document verification, and fraud rules.
              </p>
            </div>

            {/* Average Risk Score Widget */}
            <div
              className="flex items-center gap-3 px-4 py-2.5 rounded-lg self-start sm:self-auto"
              style={{
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <div>
                <p className="text-[10px] uppercase font-semibold tracking-wider" style={{ color: '#666666' }}>
                  Portfolio Avg Risk
                </p>
                <div className="flex items-baseline gap-1.5 mt-0.5">
                  <span
                    className="text-xl font-black tabular-nums"
                    style={{
                      color:
                        stats.avgRiskScore >= 70
                          ? '#FF453A'
                          : stats.avgRiskScore >= 40
                          ? '#FFB340'
                          : '#30D158',
                    }}
                  >
                    {stats.avgRiskScore}
                  </span>
                  <span className="text-xs" style={{ color: '#555555' }}>
                    / 100
                  </span>
                </div>
              </div>
              <div
                className="px-2 py-1 rounded text-xs font-semibold"
                style={{
                  background:
                    stats.avgRiskScore >= 70
                      ? 'rgba(255,69,58,0.12)'
                      : stats.avgRiskScore >= 40
                      ? 'rgba(255,179,64,0.12)'
                      : 'rgba(48,209,88,0.12)',
                  color:
                    stats.avgRiskScore >= 70
                      ? '#FF453A'
                      : stats.avgRiskScore >= 40
                      ? '#FFB340'
                      : '#30D158',
                  border: `1px solid ${
                    stats.avgRiskScore >= 70
                      ? 'rgba(255,69,58,0.25)'
                      : stats.avgRiskScore >= 40
                      ? 'rgba(255,179,64,0.25)'
                      : 'rgba(48,209,88,0.25)'
                  }`,
                }}
              >
                {stats.avgRiskScore >= 70
                  ? 'HIGH EXPOSURE'
                  : stats.avgRiskScore >= 40
                  ? 'MODERATE RISK'
                  : 'LOW EXPOSURE'}
              </div>
            </div>
          </div>

          {/* Visual Multi-segment Distribution Bar */}
          <div className="mt-5">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-medium" style={{ color: '#888888' }}>
                Classification Proportion
              </span>
              <span className="tabular-nums text-xs" style={{ color: '#555555' }}>
                {stats.totalEvaluated} Total Applications Evaluated
              </span>
            </div>

            <div
              className="h-3.5 w-full rounded-full overflow-hidden flex"
              style={{ background: 'rgba(255,255,255,0.04)' }}
            >
              {stats.highRisk > 0 && (
                <div
                  style={{
                    width: `${(stats.highRisk / stats.totalEvaluated) * 100}%`,
                    background: '#FF453A',
                  }}
                  title={`High Risk: ${stats.highRisk} (${stats.highPct}%)`}
                  className="transition-all duration-300"
                />
              )}
              {stats.mediumRisk > 0 && (
                <div
                  style={{
                    width: `${(stats.mediumRisk / stats.totalEvaluated) * 100}%`,
                    background: '#FFB340',
                  }}
                  title={`Medium Risk: ${stats.mediumRisk} (${stats.medPct}%)`}
                  className="transition-all duration-300"
                />
              )}
              {stats.lowPassCombined > 0 && (
                <div
                  style={{
                    width: `${(stats.lowPassCombined / stats.totalEvaluated) * 100}%`,
                    background: '#30D158',
                  }}
                  title={`Low Risk / Pass: ${stats.lowPassCombined} (${stats.lowPassPct}%)`}
                  className="transition-all duration-300"
                />
              )}
            </div>
          </div>

          {/* Risk Tier Detail Cards (3 Columns) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
            {/* High Risk Tier */}
            <div
              className="rounded-lg p-4 cursor-pointer transition-all duration-150"
              style={{
                background: activeFilter === 'HIGH' ? 'rgba(255,69,58,0.08)' : 'rgba(255,255,255,0.02)',
                border:
                  activeFilter === 'HIGH'
                    ? '1px solid rgba(255,69,58,0.4)'
                    : '1px solid rgba(255,255,255,0.05)',
              }}
              onClick={() => setActiveFilter(activeFilter === 'HIGH' ? 'ALL' : 'HIGH')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: '#FF453A' }} />
                  <span className="text-xs font-bold uppercase tracking-wide" style={{ color: '#FF453A' }}>
                    High Risk
                  </span>
                </div>
                <span
                  className="text-xs font-mono px-1.5 py-0.5 rounded"
                  style={{ background: 'rgba(255,69,58,0.15)', color: '#FF453A' }}
                >
                  Score 70-100
                </span>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl font-bold tabular-nums" style={{ color: '#F0F0F0' }}>
                  {stats.highRisk}
                </span>
                <span className="text-xs" style={{ color: '#666666' }}>
                  applications ({stats.highPct}%)
                </span>
              </div>
              <p className="text-xs mt-2 leading-relaxed" style={{ color: '#555555' }}>
                Critical mismatches, missing KYC docs, or severe identity discrepancies.
              </p>
            </div>

            {/* Medium Risk Tier */}
            <div
              className="rounded-lg p-4 cursor-pointer transition-all duration-150"
              style={{
                background:
                  activeFilter === 'MEDIUM' ? 'rgba(255,179,64,0.08)' : 'rgba(255,255,255,0.02)',
                border:
                  activeFilter === 'MEDIUM'
                    ? '1px solid rgba(255,179,64,0.4)'
                    : '1px solid rgba(255,255,255,0.05)',
              }}
              onClick={() => setActiveFilter(activeFilter === 'MEDIUM' ? 'ALL' : 'MEDIUM')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: '#FFB340' }} />
                  <span className="text-xs font-bold uppercase tracking-wide" style={{ color: '#FFB340' }}>
                    Medium Risk
                  </span>
                </div>
                <span
                  className="text-xs font-mono px-1.5 py-0.5 rounded"
                  style={{ background: 'rgba(255,179,64,0.15)', color: '#FFB340' }}
                >
                  Score 40-69
                </span>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl font-bold tabular-nums" style={{ color: '#F0F0F0' }}>
                  {stats.mediumRisk}
                </span>
                <span className="text-xs" style={{ color: '#666666' }}>
                  applications ({stats.medPct}%)
                </span>
              </div>
              <p className="text-xs mt-2 leading-relaxed" style={{ color: '#555555' }}>
                Partial variances, address format discrepancies, or secondary review required.
              </p>
            </div>

            {/* Low / Pass Tier */}
            <div
              className="rounded-lg p-4 cursor-pointer transition-all duration-150"
              style={{
                background:
                  activeFilter === 'LOW_PASS' ? 'rgba(48,209,88,0.08)' : 'rgba(255,255,255,0.02)',
                border:
                  activeFilter === 'LOW_PASS'
                    ? '1px solid rgba(48,209,88,0.4)'
                    : '1px solid rgba(255,255,255,0.05)',
              }}
              onClick={() => setActiveFilter(activeFilter === 'LOW_PASS' ? 'ALL' : 'LOW_PASS')}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: '#30D158' }} />
                  <span className="text-xs font-bold uppercase tracking-wide" style={{ color: '#30D158' }}>
                    Low Risk / Clean
                  </span>
                </div>
                <span
                  className="text-xs font-mono px-1.5 py-0.5 rounded"
                  style={{ background: 'rgba(48,209,88,0.15)', color: '#30D158' }}
                >
                  Score 0-39
                </span>
              </div>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-2xl font-bold tabular-nums" style={{ color: '#F0F0F0' }}>
                  {stats.lowPassCombined}
                </span>
                <span className="text-xs" style={{ color: '#666666' }}>
                  applications ({stats.lowPassPct}%)
                </span>
              </div>
              <p className="text-xs mt-2 leading-relaxed" style={{ color: '#555555' }}>
                Complete document set with high cross-document confidence and verified income.
              </p>
            </div>
          </div>
        </div>

        {/* Reports Table Section */}
        <div
          className="rounded-xl overflow-hidden"
          style={{ background: '#111111', border: '1px solid rgba(255,255,255,0.06)' }}
        >
          {/* Controls Bar (Filter Tabs + Search) */}
          <div
            className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
            style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
          >
            {/* Filter Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
              <button
                onClick={() => setActiveFilter('ALL')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150"
                style={{
                  background: activeFilter === 'ALL' ? 'rgba(170,255,0,0.12)' : 'transparent',
                  color: activeFilter === 'ALL' ? '#AAFF00' : '#666666',
                  border:
                    activeFilter === 'ALL'
                      ? '1px solid rgba(170,255,0,0.25)'
                      : '1px solid transparent',
                }}
              >
                All Reports ({reportableApps.length})
              </button>
              <button
                onClick={() => setActiveFilter('completed')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150"
                style={{
                  background: activeFilter === 'completed' ? 'rgba(48,209,88,0.12)' : 'transparent',
                  color: activeFilter === 'completed' ? '#30D158' : '#666666',
                  border:
                    activeFilter === 'completed'
                      ? '1px solid rgba(48,209,88,0.25)'
                      : '1px solid transparent',
                }}
              >
                Approved ({stats.approved})
              </button>
              <button
                onClick={() => setActiveFilter('review')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150"
                style={{
                  background: activeFilter === 'review' ? 'rgba(255,179,64,0.12)' : 'transparent',
                  color: activeFilter === 'review' ? '#FFB340' : '#666666',
                  border:
                    activeFilter === 'review'
                      ? '1px solid rgba(255,179,64,0.25)'
                      : '1px solid transparent',
                }}
              >
                Under Review ({stats.underReview})
              </button>
              <button
                onClick={() => setActiveFilter('rejected')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150"
                style={{
                  background: activeFilter === 'rejected' ? 'rgba(255,69,58,0.12)' : 'transparent',
                  color: activeFilter === 'rejected' ? '#FF453A' : '#666666',
                  border:
                    activeFilter === 'rejected'
                      ? '1px solid rgba(255,69,58,0.25)'
                      : '1px solid transparent',
                }}
              >
                Rejected ({stats.rejected})
              </button>
              <button
                onClick={() => setActiveFilter('HIGH')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150"
                style={{
                  background: activeFilter === 'HIGH' ? 'rgba(255,69,58,0.12)' : 'transparent',
                  color: activeFilter === 'HIGH' ? '#FF453A' : '#666666',
                  border:
                    activeFilter === 'HIGH'
                      ? '1px solid rgba(255,69,58,0.25)'
                      : '1px solid transparent',
                }}
              >
                High Risk ({stats.highRisk})
              </button>
            </div>

            {/* Search Input */}
            <div className="relative min-w-[240px]">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5"
                style={{ color: '#555555' }}
              />
              <input
                type="text"
                placeholder="Search by name, ID, or type..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg outline-none transition-all placeholder:text-neutral-600"
                style={{
                  background: '#0D0D0D',
                  border: '1px solid rgba(255,255,255,0.08)',
                  color: '#F0F0F0',
                }}
              />
            </div>
          </div>

          {/* Table Header */}
          <div
            className="grid grid-cols-[1.2fr_1.2fr_140px_130px_110px] gap-4 px-5 py-3 text-xs font-semibold uppercase tracking-wider"
            style={{
              color: '#444444',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <span>Application / Date</span>
            <span>Applicant / Loan Type</span>
            <span className="text-center">Risk Assessment</span>
            <span className="text-center">Decision Status</span>
            <span className="text-right">Dossier</span>
          </div>

          {/* Table Body */}
          {loading ? (
            <div className="py-20 flex justify-center">
              <Spinner size="lg" text="Loading verification reports..." />
            </div>
          ) : error ? (
            <ErrorState title="Failed to load reports" message={error} onRetry={refetch} />
          ) : filteredApps.length === 0 ? (
            <div className="py-16 text-center">
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <FileText className="h-5 w-5" style={{ color: '#555555' }} />
              </div>
              <p className="text-sm font-medium" style={{ color: '#888888' }}>
                No reports matching filter criteria
              </p>
              <p className="text-xs mt-1" style={{ color: '#444444' }}>
                Try selecting a different filter tab or clearing the search query.
              </p>
            </div>
          ) : (
            <div>
              {filteredApps.map((app) => {
                const isApproved = app.status === 'completed';
                const isRejected = app.status === 'rejected';

                const statusColor = isApproved
                  ? '#30D158'
                  : isRejected
                  ? '#FF453A'
                  : '#FFB340';

                const statusIcon = isApproved ? (
                  <CheckCircle2 className="h-3.5 w-3.5" style={{ color: '#30D158' }} />
                ) : isRejected ? (
                  <XCircle className="h-3.5 w-3.5" style={{ color: '#FF453A' }} />
                ) : (
                  <Clock className="h-3.5 w-3.5" style={{ color: '#FFB340' }} />
                );

                const riskScore = app.risk?.score ?? 0;
                const riskLevel = app.risk?.level ?? 'LOW';

                return (
                  <div
                    key={app.application_id}
                    className="group grid grid-cols-[1.2fr_1.2fr_140px_130px_110px] gap-4 px-5 py-4 items-center cursor-pointer transition-all duration-150"
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                    onClick={() => navigate(`/applications/${app.application_id}/report`)}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLDivElement).style.background = 'rgba(255,255,255,0.02)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLDivElement).style.background = 'transparent';
                    }}
                  >
                    {/* App ID + Submission Date */}
                    <div>
                      <span
                        className="font-mono text-xs font-semibold px-2 py-0.5 rounded inline-block"
                        style={{
                          background: 'rgba(170,255,0,0.08)',
                          color: '#AAFF00',
                          border: '1px solid rgba(170,255,0,0.15)',
                        }}
                      >
                        {app.application_id}
                      </span>
                      <p className="text-xs mt-1.5" style={{ color: '#444444' }}>
                        {formatDate(app.updated_at || app.created_at)}
                      </p>
                    </div>

                    {/* Applicant Name + Loan Type */}
                    <div>
                      <p className="text-sm font-semibold" style={{ color: '#F0F0F0' }}>
                        {app.applicant_name}
                      </p>
                      <p className="text-xs mt-0.5" style={{ color: '#555555' }}>
                        {app.loan_type}
                      </p>
                    </div>

                    {/* Risk Assessment (Score + Level badge) */}
                    <div className="flex flex-col items-center justify-center gap-1">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs font-bold" style={{ color: '#D0D0D0' }}>
                          {riskScore}/100
                        </span>
                        <RiskBadge level={riskLevel} />
                      </div>
                      {app.risk?.flags && app.risk.flags.length > 0 ? (
                        <span className="text-[10px]" style={{ color: '#666666' }}>
                          {app.risk.flags.length} flag{app.risk.flags.length > 1 ? 's' : ''} detected
                        </span>
                      ) : (
                        <span className="text-[10px]" style={{ color: '#30D158' }}>
                          Zero flags
                        </span>
                      )}
                    </div>

                    {/* Decision Status */}
                    <div className="flex items-center justify-center gap-1.5">
                      {statusIcon}
                      <span className="text-xs font-semibold capitalize" style={{ color: statusColor }}>
                        {app.status === 'completed'
                          ? 'Approved'
                          : app.status === 'rejected'
                          ? 'Rejected'
                          : 'Under Review'}
                      </span>
                    </div>

                    {/* View report button */}
                    <div className="flex justify-end">
                      <button
                        className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-150 group-hover:bg-[#AAFF00] group-hover:text-black"
                        style={{
                          background: 'rgba(170,255,0,0.08)',
                          color: '#AAFF00',
                          border: '1px solid rgba(170,255,0,0.2)',
                        }}
                      >
                        View Dossier
                        <ArrowUpRight className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

