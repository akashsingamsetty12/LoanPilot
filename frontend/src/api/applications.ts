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
  const response = await apiClient.get<Application[]>('/applications');
  return response.data;
}

export async function getApplication(id: string): Promise<Application> {
  if (useMock) {
    await delay(500);
    const app = mockApplications.find(a => a.application_id === id);
    if (!app) throw new Error(`Application ${id} not found`);
    return app;
  }
  const response = await apiClient.get<Application>(`/applications/${id}`);
  return response.data;
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
    return newApp;
  }
  const response = await apiClient.post<Application>('/applications', data);
  return response.data;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  if (useMock) {
    await delay(400);
    return getMockStats();
  }
  const response = await apiClient.get<DashboardStats>('/applications/stats');
  return response.data;
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
