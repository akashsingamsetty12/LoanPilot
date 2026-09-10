/**
 * Constants
 * ==========
 * Status enums, severity colors, document type labels used across components.
 */

// Application status progression
export const APP_STATUS = {
  CREATED: 'created',
  DOCUMENTS_UPLOADED: 'documents_uploaded',
  PROCESSING: 'processing',
  REVIEW: 'review',
  DECIDED: 'decided',
};

// Document processing status
export const DOC_STATUS = {
  UPLOADED: 'uploaded',
  OCR_PROCESSING: 'ocr_processing',
  OCR_COMPLETE: 'ocr_complete',
  CLASSIFYING: 'classifying',
  CLASSIFIED: 'classified',
  EXTRACTING: 'extracting',
  EXTRACTED: 'extracted',
  FAILED: 'failed',
};

// Document types
export const DOC_TYPES = {
  PAYSLIP: 'payslip',
  BANK_STATEMENT: 'bank_statement',
  TAX_RETURN: 'tax_return',
  KYC_IDENTITY: 'kyc_identity',
  ADDRESS_PROOF: 'address_proof',
  OTHER: 'other',
  UNCLASSIFIED: 'unclassified',
};

// Document type display labels
export const DOC_TYPE_LABELS = {
  payslip: 'Payslip',
  bank_statement: 'Bank Statement',
  tax_return: 'Tax Return',
  kyc_identity: 'KYC / Identity',
  address_proof: 'Address Proof',
  other: 'Other',
  unclassified: 'Unclassified',
};

// Risk severity levels and their colors
export const SEVERITY_CONFIG = {
  HIGH:   { label: 'High',   color: '#EF4444', bg: '#FEF2F2', border: '#FECACA' },
  MEDIUM: { label: 'Medium', color: '#F59E0B', bg: '#FFFBEB', border: '#FDE68A' },
  LOW:    { label: 'Low',    color: '#3B82F6', bg: '#EFF6FF', border: '#BFDBFE' },
  PASS:   { label: 'Pass',   color: '#10B981', bg: '#ECFDF5', border: '#A7F3D0' },
};

// Risk level thresholds
export const RISK_LEVELS = {
  LOW: { min: 0, max: 30, label: 'Low Risk', color: '#10B981' },
  MEDIUM: { min: 31, max: 60, label: 'Medium Risk', color: '#F59E0B' },
  HIGH: { min: 61, max: 100, label: 'High Risk', color: '#EF4444' },
};
