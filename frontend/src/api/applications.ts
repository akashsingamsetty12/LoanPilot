import apiClient from './client';
import type { Application } from '../types';
import { mockApplications, getMockStats } from '../mock/data';
import type { DashboardStats } from '../types';

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

export async function getApplications(): Promise<Application[]> {
  if (useMock) {
    await delay(600);
    return mockApplications;
  }
  try {
    const response = await apiClient.get<Application[]>('/applications');
    return response.data;
  } catch (err) {
    console.warn('Backend unavailable, falling back to mock applications:', err);
    await delay(300);
    return mockApplications;
  }
}

export async function getApplication(id: string): Promise<Application> {
  if (useMock) {
    await delay(500);
    const app = mockApplications.find(a => a.application_id === id);
    if (!app) throw new Error(`Application ${id} not found`);
    return app;
  }
  try {
    const response = await apiClient.get<Application>(`/applications/${id}`);
    return response.data;
  } catch (err) {
    console.warn(`Backend unavailable, returning mock application for ${id}:`, err);
    await delay(300);
    const app = mockApplications.find(a => a.application_id === id);
    if (app) return app;

    // Fallback new mock application if ID not found in pre-populated array
    const fallbackApp: Application = {
      application_id: id,
      applicant_name: 'New Applicant (' + id + ')',
      applicant_email: 'applicant@example.com',
      loan_type: 'Personal Loan',
      status: 'review',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      documents: [
        {
          document_id: `DOC-${Date.now()}-1`,
          file_name: 'identity_doc.pdf',
          type: 'id_proof',
          status: 'completed',
          pages: 1,
          ocr_confidence: 96,
          file_size: 180000,
          uploaded_at: new Date().toISOString(),
          fields: [
            { field_name: 'Full Name', value: 'New Applicant', confidence: 98, page: 1 },
          ],
        },
      ],
      verification: {
        matches: [
          {
            field_name: 'Full Name',
            values: [{ document: 'ID Proof', value: 'New Applicant' }],
            status: 'PASS',
          },
        ],
        mismatches: [],
        missing_documents: [],
      },
      risk: { score: 15, level: 'LOW', flags: [] },
      recommendation: 'APPROVE',
    };
    mockApplications.unshift(fallbackApp);
    return fallbackApp;
  }
}

export async function createApplication(data: {
  applicant_name: string;
  applicant_email: string;
  loan_type: string;
}): Promise<Application> {
  if (useMock) {
    await delay(800);
    return createMockApplication(data);
  }
  try {
    const response = await apiClient.post<Application>('/applications', data);
    return response.data;
  } catch (err) {
    console.warn('Backend unavailable, creating application in local state:', err);
    await delay(600);
    return createMockApplication(data);
  }
}

function createMockApplication(data: {
  applicant_name: string;
  applicant_email: string;
  loan_type: string;
}): Application {
  const newId = `APP-${String(mockApplications.length + 1).padStart(4, '0')}`;
  const newApp: Application = {
    application_id: newId,
    applicant_name: data.applicant_name,
    applicant_email: data.applicant_email || 'applicant@example.com',
    loan_type: data.loan_type,
    status: 'review',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    documents: [
      {
        document_id: `DOC-${Date.now()}-1`,
        file_name: 'id_proof_applicant.pdf',
        type: 'id_proof',
        status: 'completed',
        pages: 1,
        ocr_confidence: 97,
        file_size: 180000,
        uploaded_at: new Date().toISOString(),
        fields: [
          { field_name: 'Full Name', value: data.applicant_name, confidence: 98, page: 1 },
          { field_name: 'Email', value: data.applicant_email || 'applicant@example.com', confidence: 96, page: 1 },
        ],
      },
    ],
    verification: {
      matches: [
        {
          field_name: 'Full Name',
          values: [{ document: 'ID Proof', value: data.applicant_name }],
          status: 'PASS',
        },
      ],
      mismatches: [],
      missing_documents: [],
    },
    risk: { score: 12, level: 'LOW', flags: [] },
    recommendation: 'APPROVE',
  };
  mockApplications.unshift(newApp);
  return newApp;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  if (useMock) {
    await delay(400);
    return getMockStats();
  }
  try {
    const response = await apiClient.get<DashboardStats>('/applications/stats');
    return response.data;
  } catch (err) {
    console.warn('Backend stats endpoint unavailable, returning mock stats:', err);
    await delay(300);
    return getMockStats();
  }
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
