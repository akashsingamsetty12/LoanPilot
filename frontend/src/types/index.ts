// ─── Document Types ───

export interface ExtractedField {
  field_name: string;
  value: string;
  confidence: number;
  page: number;
}

export type DocumentType =
  | 'payslip'
  | 'bank_statement'
  | 'tax_return'
  | 'id_proof'
  | 'address_proof'
  | 'employment_letter'
  | 'other';

export type DocumentStatus =
  | 'uploaded'
  | 'processing'
  | 'completed'
  | 'failed';

export interface LoanDocument {
  document_id: string;
  file_name: string;
  type: DocumentType;
  status: DocumentStatus;
  pages: number;
  ocr_confidence: number;
  file_size: number;
  uploaded_at: string;
  fields: ExtractedField[];
}

// ─── Risk & Verification Types ───

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW' | 'PASS';

export interface RiskFlag {
  id: string;
  severity: RiskLevel;
  reason: string;
  details: string;
  evidence: {
    document: string;
    page: number;
    value?: string;
  }[];
}

export interface Risk {
  score: number;
  level: RiskLevel;
  flags: RiskFlag[];
}

export type ComparisonStatus = 'PASS' | 'MISMATCH' | 'MISSING';

export interface ComparisonField {
  field_name: string;
  values: {
    document: string;
    value: string;
  }[];
  status: ComparisonStatus;
}

export interface Verification {
  matches: ComparisonField[];
  mismatches: ComparisonField[];
  missing_documents: string[];
}

export type LoanType = 'PERSONAL_LOAN' | 'HOME_LOAN' | 'AUTO_LOAN' | 'BUSINESS_LOAN';

export type ApplicationStatus =
  | 'draft'
  | 'uploading'
  | 'processing'
  | 'review'
  | 'completed'
  | 'rejected';

export type Recommendation =
  | 'NEEDS_HUMAN_REVIEW'
  | 'APPROVE'
  | 'REJECT'
  | 'INSUFFICIENT_DATA';

export interface Application {
  application_id: string;
  applicant_name: string;
  applicant_email: string;
  loan_type: string;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
  documents: LoanDocument[];
  verification: Verification;
  risk: Risk;
  recommendation: Recommendation;
}

export interface ApplicationSummary {
  application_id: string;
  applicant_name: string;
  status: ApplicationStatus;
  document_count: number;
  total_documents: number;
  risk_level: RiskLevel;
  updated_at: string;
}

// ─── Chat Types ───

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface AgentQuery {
  query: string;
  application_id: string;
}

export interface AgentResponse {
  response: string;
  sources?: {
    document: string;
    page: number;
  }[];
}

// ─── Report Types ───

export interface VerificationReport {
  application_id: string;
  applicant_name: string;
  generated_at: string;
  documents_reviewed: number;
  risk_score: number;
  risk_level: RiskLevel;
  flags: RiskFlag[];
  verification_results: ComparisonField[];
  missing_documents: string[];
  recommendation: Recommendation;
}

// ─── Dashboard Types ───

export interface DashboardStats {
  total: number;
  pending: number;
  needs_attention: number;
  completed: number;
}
