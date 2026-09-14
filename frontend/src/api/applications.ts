import apiClient from './client';
import type { Application, DashboardStats } from '../types';
import { mockApplications, getMockStats } from '../mock/data';

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

function normalizeApplication(data: any): Application {
  const appId = data.application_id || data.id || 'APP-0001';

  // Format documents (deduplicating by filename)
  const rawDocs = data.documents || [];
  const seenFileNames = new Set<string>();
  const uniqueDocs: any[] = [];
  for (const d of rawDocs) {
    const fn = (d.file_name || d.filename || d.document_id || d.id || '').toLowerCase();
    if (fn && seenFileNames.has(fn)) continue;
    if (fn) seenFileNames.add(fn);
    uniqueDocs.push(d);
  }

  const docs = uniqueDocs.map((d: any) => ({
    document_id: d.document_id || d.id || '',
    file_name: d.file_name || d.filename || '',
    type: d.type || d.doc_type || 'other',
    status: d.status || 'completed',
    pages: d.pages || 1,
    ocr_confidence: Math.round((d.ocr_confidence || 0) <= 1 ? (d.ocr_confidence || 0.9) * 100 : d.ocr_confidence),
    file_size: d.file_size || 1024,
    uploaded_at: d.uploaded_at || d.created_at || new Date().toISOString(),
    fields: (() => {
      if (Array.isArray(d.fields) && d.fields.length > 0) {
        return d.fields.map((f: any) => {
          let val = f.value;
          if (val && typeof val === 'object') {
            val = val.value !== undefined ? val.value : null;
          }
          const displayVal = (val === null || val === undefined || String(val).trim() === '' || String(val).trim() === '[object Object]')
            ? 'Not Detected'
            : String(val);
          const rawConf = typeof f.confidence === 'number' ? f.confidence : (f.value?.confidence ?? 0.9);
          const conf = Math.round(rawConf <= 1 ? rawConf * 100 : rawConf);
          return {
            field_name: f.field_name || 'Field',
            value: displayVal,
            confidence: conf,
            page: f.page || f.value?.page || 1
          };
        });
      }

      if (d.extracted_fields && typeof d.extracted_fields === 'object') {
        return Object.entries(d.extracted_fields).map(([k, v]: [string, any]) => {
          let val = v;
          let conf = 0.9;
          let page = 1;

          if (v && typeof v === 'object') {
            val = v.value;
            conf = typeof v.confidence === 'number' ? v.confidence : 0.9;
            page = v.page || 1;
          }

          const displayVal = (val === null || val === undefined || String(val).trim() === '' || String(val).trim() === '[object Object]')
            ? 'Not Detected'
            : String(val);
          const confPercent = Math.round(conf <= 1 ? conf * 100 : conf);

          return {
            field_name: k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            value: displayVal,
            confidence: confPercent,
            page: page
          };
        });
      }

      return [];
    })()
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

  const mismatches = (ver.mismatches || [])
    .filter((m: any) => m.field !== 'document_completeness')
    .map((m: any) => typeof m === 'object' && m.field ? {
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
      flags: (() => {
        const seenFlags = new Set<string>();
        const mappedFlags: any[] = [];

        for (let idx = 0; idx < rawFlags.length; idx++) {
          const f = rawFlags[idx];
          const severity = f.severity || 'LOW';
          let rawReason = f.reason || 'Verification finding';
          let details = '';
          let points = 0;
          let evidenceDoc = 'Document';
          let evidenceVal = '';

          let dObj: any = f.details;
          if (typeof dObj === 'string' && dObj.trim().startsWith('{')) {
            try { dObj = JSON.parse(dObj); } catch {}
          }

          // Skip redundant generic findings for missing documents already handled
          if (
            (rawReason.toLowerCase().includes('inconsistency') || rawReason.toLowerCase().includes('document completeness')) &&
            dObj &&
            typeof dObj === 'object' &&
            (dObj.field === 'document_completeness' || String(dObj.evidence || '').toLowerCase().includes('missing'))
          ) {
            continue;
          }

          if (typeof dObj === 'object' && dObj !== null) {
            points = dObj.points || 0;
            if (dObj.evidence) {
              details = String(dObj.evidence);
            } else if (dObj.field && dObj.field !== 'document_completeness') {
              const cleanField = String(dObj.field).replace(/_/g, ' ');
              details = `Discrepancy identified in ${cleanField} across submitted records.`;
            } else if (rawReason.toLowerCase().includes('missing')) {
              details = 'This required verification document was not found in the application submission.';
            } else {
              details = 'Verification inconsistency flagged by automated rule engine.';
            }
          } else if (typeof dObj === 'string' && dObj.trim()) {
            details = dObj.trim();
          } else {
            details = f.evidence || 'Requires manual underwriter confirmation.';
          }

          // Clean up title & evidence for missing docs
          let cleanReason = rawReason;
          if (rawReason.toLowerCase().includes('missing required document:')) {
            const docType = rawReason.split(':').slice(1).join(':').trim();
            const cleanDoc = docType.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
            cleanReason = `Missing Document: ${cleanDoc}`;
            evidenceDoc = cleanDoc;
            evidenceVal = 'Mandatory verification document is missing from this loan file.';
          } else if (f.field && f.field !== 'document_completeness') {
            const fieldLabel = f.field.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
            cleanReason = `${fieldLabel} Mismatch`;
            evidenceDoc = fieldLabel;
            evidenceVal = details;
          } else {
            evidenceDoc = 'Verification Rule';
            evidenceVal = details;
          }

          const dedupeKey = cleanReason.toLowerCase();
          if (seenFlags.has(dedupeKey)) continue;
          seenFlags.add(dedupeKey);

          mappedFlags.push({
            id: String(mappedFlags.length + 1),
            severity: severity as any,
            reason: cleanReason,
            details: points > 0 ? `${details} (Risk penalty: +${points} pts)` : details,
            evidence: [{ document: evidenceDoc, page: 1, value: evidenceVal }]
          });
        }

        return mappedFlags;
      })()
    },
    recommendation: data.recommendation || 'NEEDS_HUMAN_REVIEW'
  };
}

export async function getApplications(): Promise<Application[]> {
  if (useMock) {
    await delay(600);
    return mockApplications;
  }
  try {
    const response = await apiClient.get<any>('/applications');
    const rawList = Array.isArray(response.data) ? response.data : (response.data?.applications || []);
    return rawList.map((app: any) => normalizeApplication(app));
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
    const response = await apiClient.get<any>(`/applications/${id}`);
    return normalizeApplication(response.data);
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
    const response = await apiClient.post<any>('/applications', {
      applicant_name: data.applicant_name,
      kaggle_loan_id: null,
    });
    return normalizeApplication(response.data);
  } catch (err) {
    console.warn('Backend unavailable, creating application in local state:', err);
    await delay(600);
    return createMockApplication(data);
  }
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
    try {
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
    } catch {
      console.warn('Backend stats endpoint unavailable, returning mock stats:', err);
      await delay(300);
      return getMockStats();
    }
  }
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
