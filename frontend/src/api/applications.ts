import apiClient from './client';
import type { Application, DashboardStats } from '../types';
import { mockApplications, getMockStats } from '../mock/data';

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

function normalizeApplication(data: any): Application {
  const appId = data.application_id || data.id || 'APP-0001';

  // Format documents
  const docs = (data.documents || []).map((d: any) => ({
    document_id: d.document_id || d.id || '',
    file_name: d.file_name || d.filename || '',
    type: d.type || d.doc_type || 'other',
    status: d.status || 'completed',
    pages: d.pages || 1,
    ocr_confidence: Math.round((d.ocr_confidence || 0) <= 1 ? (d.ocr_confidence || 0.9) * 100 : d.ocr_confidence),
    file_size: d.file_size || 1024,
    uploaded_at: d.uploaded_at || d.created_at || new Date().toISOString(),
    fields: d.fields || (d.extracted_fields ? Object.entries(d.extracted_fields).map(([k, v]: [string, any]) => ({
      field_name: k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: String(v?.value ?? v ?? ''),
      confidence: Math.round((v?.confidence ?? 0.9) <= 1 ? (v?.confidence ?? 0.9) * 100 : (v?.confidence ?? 90)),
      page: v?.page ?? 1
    })) : [])
  }));

  // Format risk
  const riskScore = data.risk?.score ?? data.risk_score ?? 0;
  const riskLevel = data.risk?.level ?? data.risk_level ?? 'LOW';
  const rawFlags = data.risk?.flags || data.flags || [];

  // Format verification
  const ver = data.verification || {};
  const matches = (ver.matches || []).map((m: any) => typeof m === 'string' ? {
    field_name: m.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
    values: [{ document: 'Verified', value: 'Consistent' }],
    status: 'PASS' as const
  } : m);

  const mismatches = (ver.mismatches || []).map((m: any) => typeof m === 'object' && m.field ? {
    field_name: m.field.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
    values: [
      { document: m.sources?.[0] || 'Source A', value: String(m.values?.[0] ?? '') },
      { document: m.sources?.[1] || 'Source B', value: String(m.values?.[1] ?? '') }
    ],
    status: 'MISMATCH' as const
  } : m);

  const missingDocs = ver.missing_documents || [];

  return {
    application_id: appId,
    applicant_name: data.applicant_name || 'Applicant',
    applicant_email: data.applicant_email || 'applicant@example.com',
    loan_type: data.loan_type || 'Home Loan',
    status: data.status || 'draft',
    created_at: data.created_at || new Date().toISOString(),
    updated_at: data.updated_at || new Date().toISOString(),
    documents: docs,
    verification: {
      matches: matches,
      mismatches: mismatches,
      missing_documents: missingDocs
    },
    risk: {
      score: riskScore,
      level: riskLevel,
      flags: rawFlags.map((f: any, idx: number) => ({
        id: String(idx + 1),
        severity: f.severity || 'LOW',
        reason: f.reason || 'Verification finding',
        details: f.details ? JSON.stringify(f.details) : (f.evidence || ''),
        evidence: [{ document: f.evidence || 'Document', page: 1, value: f.reason || '' }]
      }))
    },
    recommendation: data.recommendation || 'NEEDS_HUMAN_REVIEW'
  };
}

export async function getApplications(): Promise<Application[]> {
  if (useMock) {
    await delay(600);
    return mockApplications;
  }
  const response = await apiClient.get<any>('/applications');
  const rawList = Array.isArray(response.data) ? response.data : (response.data?.applications || []);
  return rawList.map((app: any) => normalizeApplication(app));
}

export async function getApplication(id: string): Promise<Application> {
  if (useMock) {
    await delay(500);
    const app = mockApplications.find(a => a.application_id === id);
    if (!app) throw new Error(`Application ${id} not found`);
    return app;
  }
  const response = await apiClient.get<any>(`/applications/${id}`);
  return normalizeApplication(response.data);
}

export async function createApplication(data: {
  applicant_name: string;
  applicant_email: string;
  loan_type: string;
}): Promise<Application> {
  if (useMock) {
    await delay(800);
    const newApp: Application = {
      application_id: `APP-${String(mockApplications.length + 1).padStart(4, '0')}`,
      applicant_name: data.applicant_name,
      applicant_email: data.applicant_email,
      loan_type: data.loan_type,
      status: 'draft',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      documents: [],
      verification: { matches: [], mismatches: [], missing_documents: [] },
      risk: { score: 0, level: 'LOW', flags: [] },
      recommendation: 'INSUFFICIENT_DATA',
    };
    mockApplications.unshift(newApp);
    return newApp;
  }
  const response = await apiClient.post<any>('/applications', {
    applicant_name: data.applicant_name,
    kaggle_loan_id: null,
  });
  return normalizeApplication(response.data);
}

export async function decideApplication(
  id: string,
  data: {
    decision: 'approved' | 'rejected' | 'needs_more_info';
    notes?: string;
    decided_by?: string;
  }
): Promise<any> {
  const response = await apiClient.patch(`/applications/${id}/decide`, data);
  return response.data;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  if (useMock) {
    await delay(400);
    return getMockStats();
  }
  try {
    const response = await apiClient.get<DashboardStats>('/applications/stats');
    return response.data;
  } catch {
    const apps = await getApplications();
    const total = apps.length;
    const review = apps.filter(a => a.status === 'review').length;
    const completed = apps.filter(a => a.status === 'completed').length;
    const highRisk = apps.filter(a => a.risk?.level === 'HIGH').length;
    return {
      total,
      pending: review,
      needs_attention: highRisk,
      completed,
    };
  }
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

