import type { ApplicationStatus, ComparisonStatus, DocumentType, RiskLevel } from '../types';

/**
 * Utility function to conditionally join Tailwind class names.
 */
export function classNames(...classes: (string | undefined | null | false | boolean)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Color mappings for risk levels.
 */
export function getRiskColor(level?: RiskLevel | string): { text: string; bg: string; border: string } {
  switch (level?.toUpperCase()) {
    case 'HIGH':
      return { text: 'text-risk-high', bg: 'bg-risk-high-bg', border: 'border-risk-high-border' };
    case 'MEDIUM':
      return { text: 'text-risk-medium', bg: 'bg-risk-medium-bg', border: 'border-risk-medium-border' };
    case 'LOW':
      return { text: 'text-risk-low', bg: 'bg-risk-low-bg', border: 'border-risk-low-border' };
    case 'PASS':
      return { text: 'text-risk-pass', bg: 'bg-risk-pass-bg', border: 'border-risk-pass-border' };
    default:
      return { text: 'text-charcoal-secondary', bg: 'bg-surface-100', border: 'border-surface-300' };
  }
}

/**
 * Color mappings for application statuses.
 */
export function getStatusColor(status?: ApplicationStatus | string): { text: string; bg: string; border: string } {
  switch (status?.toLowerCase()) {
    case 'draft':
      return { text: 'text-charcoal-muted', bg: 'bg-white/[0.03]', border: 'border-white/10' };
    case 'uploading':
    case 'processing':
      return { text: 'text-primary-300', bg: 'bg-primary-300/10', border: 'border-primary-300/20' };
    case 'review':
      return { text: 'text-risk-medium', bg: 'bg-risk-medium-bg', border: 'border-risk-medium-border' };
    case 'completed':
      return { text: 'text-risk-low', bg: 'bg-risk-low-bg', border: 'border-risk-low-border' };
    case 'rejected':
      return { text: 'text-risk-high', bg: 'bg-risk-high-bg', border: 'border-risk-high-border' };
    default:
      return { text: 'text-charcoal-secondary', bg: 'bg-white/[0.03]', border: 'border-white/10' };
  }
}

/**
 * User-friendly labels for application statuses.
 */
export function getStatusLabel(status?: ApplicationStatus | string): string {
  switch (status?.toLowerCase()) {
    case 'draft':
      return 'Draft';
    case 'uploading':
      return 'Uploading';
    case 'processing':
      return 'Processing';
    case 'review':
      return 'Under Review';
    case 'completed':
      return 'Completed';
    case 'rejected':
      return 'Rejected';
    default:
      return status ? status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ') : 'Unknown';
  }
}

/**
 * Color mappings for cross-document comparison statuses.
 */
export function getComparisonColor(status?: ComparisonStatus | string): { text: string; bg: string; border: string } {
  switch (status?.toUpperCase()) {
    case 'PASS':
      return { text: 'text-risk-low', bg: 'bg-risk-low-bg', border: 'border-risk-low-border' };
    case 'MISMATCH':
      return { text: 'text-risk-high', bg: 'bg-risk-high-bg', border: 'border-risk-high-border' };
    case 'MISSING':
      return { text: 'text-risk-medium', bg: 'bg-risk-medium-bg', border: 'border-risk-medium-border' };
    default:
      return { text: 'text-charcoal-secondary', bg: 'bg-surface-100', border: 'border-surface-300' };
  }
}

/**
 * User-friendly labels for document types.
 */
export function getDocumentTypeLabel(type?: DocumentType | string): string {
  const map: Record<string, string> = {
    payslip: 'Payslip',
    bank_statement: 'Bank Statement',
    tax_return: 'Tax Return',
    id_proof: 'ID Proof',
    kyc_identity: 'KYC / Identity',
    address_proof: 'Address Proof',
    employment_letter: 'Employment Letter',
    other: 'Other',
    unclassified: 'Unclassified',
  };
  if (!type) return 'Unknown';
  return map[type.toLowerCase()] || type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Format a date string or Date object into human-readable date.
 * e.g. "15 Aug 2024"
 */
export function formatDate(dateString?: string | Date | null): string {
  if (!dateString) return '—';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return '—';
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return '—';
  }
}

/**
 * Format a date string or Date object into human-readable datetime.
 * e.g. "15 Aug 2024, 10:30 AM"
 */
export function formatDateTime(dateString?: string | Date | null): string {
  if (!dateString) return '—';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return '—';
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '—';
  }
}

/**
 * Format byte count into human-readable file size (B, KB, MB, GB).
 */
export function formatFileSize(bytes?: number | null): string {
  if (bytes == null || isNaN(bytes)) return '—';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return `${size.toFixed(1)} ${units[i]}`;
}

/**
 * Format a number as Indian currency (INR).
 */
export function formatCurrency(value?: number | null): string {
  if (value == null || isNaN(value)) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format confidence score as a percentage.
 */
export function formatConfidence(confidence?: number | null): string {
  if (confidence == null || isNaN(confidence)) return '—';
  const val = confidence <= 1 ? confidence * 100 : confidence;
  return `${Math.round(val)}%`;
}
