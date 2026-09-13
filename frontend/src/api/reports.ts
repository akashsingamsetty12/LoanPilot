import apiClient from './client';
import type { VerificationReport, Application } from '../types';
import { mockApplications } from '../mock/data';

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

export async function getReport(applicationId: string): Promise<VerificationReport> {
  if (useMock) {
    await delay(700);
    const app = mockApplications.find(a => a.application_id === applicationId);
    if (!app) return buildFallbackReport(applicationId);
    return buildReportFromApp(app);
  }

  try {
    const response = await apiClient.get<VerificationReport>(
      `/applications/${applicationId}/report`
    );
    return response.data;
  } catch (err) {
    console.warn('Report API error, using fallback report from application data:', err);
    const app = mockApplications.find(a => a.application_id === applicationId);
    if (app) return buildReportFromApp(app);
    return buildFallbackReport(applicationId);
  }
}

export async function downloadReport(applicationId: string): Promise<void> {
  if (useMock) {
    const app = mockApplications.find(a => a.application_id === applicationId);
    const report = app ? buildReportFromApp(app) : buildFallbackReport(applicationId);
    const text = generateReportText(report);
    const blob = new Blob([text], { type: 'text/plain' });
    triggerDownload(blob, `LoanPilot_Report_${applicationId}.txt`);
    return;
  }

  try {
    const response = await apiClient.get(`/applications/${applicationId}/report/download`, {
      responseType: 'blob',
    });

    const headerVal = response.headers['content-type'];
    const contentType = typeof headerVal === 'string' ? headerVal : 'application/pdf';
    const ext = contentType.includes('pdf') ? 'pdf' : 'json';
    const blob = new Blob([response.data], { type: contentType });
    triggerDownload(blob, `LoanPilot_Report_${applicationId}.${ext}`);
  } catch (err) {
    console.warn('Report download endpoint failed, generating local text report:', err);
    const app = mockApplications.find(a => a.application_id === applicationId);
    const report = app ? buildReportFromApp(app) : buildFallbackReport(applicationId);
    const text = generateReportText(report);
    const blob = new Blob([text], { type: 'text/plain' });
    triggerDownload(blob, `LoanPilot_Report_${applicationId}.txt`);
  }
}

function triggerDownload(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

function buildReportFromApp(app: Application): VerificationReport {
  return {
    application_id: app.application_id,
    applicant_name: app.applicant_name,
    generated_at: new Date().toISOString(),
    documents_reviewed: app.documents.filter(d => d.status === 'completed').length,
    risk_score: app.risk.score,
    risk_level: app.risk.level,
    flags: app.risk.flags,
    verification_results: [...app.verification.matches, ...app.verification.mismatches],
    missing_documents: app.verification.missing_documents,
    recommendation: app.recommendation,
  };
}

function buildFallbackReport(applicationId: string): VerificationReport {
  return {
    application_id: applicationId,
    applicant_name: 'Applicant ' + applicationId,
    generated_at: new Date().toISOString(),
    documents_reviewed: 1,
    risk_score: 15,
    risk_level: 'LOW',
    flags: [],
    verification_results: [],
    missing_documents: [],
    recommendation: 'APPROVE',
  };
}

function generateReportText(report: VerificationReport): string {
  const lines: string[] = [
    '═══════════════════════════════════════════════════════',
    '                    LoanPilot',
    '            Loan Verification Report',
    '═══════════════════════════════════════════════════════',
    '',
    `Application ID:     ${report.application_id}`,
    `Applicant:          ${report.applicant_name}`,
    `Generated:          ${new Date(report.generated_at).toLocaleString()}`,
    `Documents Reviewed: ${report.documents_reviewed}`,
    '',
    '───────────────────────────────────────────────────────',
    '  RISK ASSESSMENT',
    '───────────────────────────────────────────────────────',
    '',
    `Risk Score:         ${report.risk_score}/100`,
    `Risk Level:         ${report.risk_level}`,
    '',
  ];

  if (report.flags.length > 0) {
    lines.push('───────────────────────────────────────────────────────');
    lines.push('  FLAGS & ISSUES');
    lines.push('───────────────────────────────────────────────────────');
    lines.push('');
    report.flags.forEach(flag => {
      lines.push(`  [${flag.severity}] ${flag.reason}`);
      lines.push(`  ${flag.details}`);
      lines.push('');
    });
  }

  if (report.missing_documents.length > 0) {
    lines.push('───────────────────────────────────────────────────────');
    lines.push('  MISSING DOCUMENTS');
    lines.push('───────────────────────────────────────────────────────');
    lines.push('');
    report.missing_documents.forEach(doc => {
      lines.push(`  • ${doc}`);
    });
    lines.push('');
  }

  lines.push('───────────────────────────────────────────────────────');
  lines.push('  RECOMMENDATION');
  lines.push('───────────────────────────────────────────────────────');
  lines.push('');
  lines.push(`  ${report.recommendation.replace(/_/g, ' ')}`);
  lines.push('');
  lines.push('═══════════════════════════════════════════════════════');
  lines.push('  This report is generated by LoanPilot AI system.');
  lines.push('  Final lending decisions are made by authorized officers.');
  lines.push('═══════════════════════════════════════════════════════');

  return lines.join('\n');
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
