/**
 * Formatters
 * ===========
 * Utility functions for formatting currency, dates, percentages.
 */

/**
 * Format a number as Indian currency (₹).
 * e.g. 900000 → "₹9,00,000"
 */
export const formatCurrency = (value) => {
  if (value == null) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
};

/**
 * Format a confidence score as a percentage.
 * e.g. 0.97 → "97%"
 */
export const formatConfidence = (confidence) => {
  if (confidence == null) return '—';
  return `${Math.round(confidence * 100)}%`;
};

/**
 * Format an ISO datetime string.
 * e.g. "2024-08-15T10:30:00Z" → "15 Aug 2024, 10:30 AM"
 */
export const formatDate = (dateString) => {
  if (!dateString) return '—';
  return new Date(dateString).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Format file size in human-readable form.
 * e.g. 1048576 → "1.0 MB"
 */
export const formatFileSize = (bytes) => {
  if (!bytes) return '—';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let size = bytes;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return `${size.toFixed(1)} ${units[i]}`;
};
