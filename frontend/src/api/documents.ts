import apiClient from './client';
import { mockApplications } from '../mock/data';

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

export interface UploadResult {
  document_id: string;
  file_name: string;
  status: 'uploaded' | 'failed';
}

export async function uploadDocuments(
  applicationId: string,
  files: File[]
): Promise<UploadResult[]> {
  if (useMock) {
    await delay(1500);
    const results = files.map((file, i) => ({
      document_id: `DOC-MOCK-${Date.now()}-${i}`,
      file_name: file.name,
      status: 'uploaded' as const,
    }));

    const app = mockApplications.find(a => a.application_id === applicationId);
    if (app) {
      files.forEach((file, i) => {
        const lower = file.name.toLowerCase();
        let docType: 'payslip' | 'bank_statement' | 'tax_return' | 'kyc_identity' | 'address_proof' = 'kyc_identity';
        if (lower.includes('payslip') || lower.includes('salary')) docType = 'payslip';
        else if (lower.includes('bank') || lower.includes('statement')) docType = 'bank_statement';
        else if (lower.includes('tax') || lower.includes('itr')) docType = 'tax_return';
        else if (lower.includes('address') || lower.includes('bill')) docType = 'address_proof';

        app.documents.push({
          document_id: `DOC-${String(app.documents.length + 1).padStart(3, '0')}`,
          file_name: file.name,
          type: docType,
          status: 'completed',
          pages: 2,
          ocr_confidence: 94,
          file_size: file.size,
          uploaded_at: new Date().toISOString(),
          fields: [
            { field_name: 'Applicant Name', value: app.applicant_name, confidence: 97, page: 1 }
          ]
        });
      });
      app.status = 'review';
    }

    return results;
  }

  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await apiClient.post<UploadResult[]>(
    `/applications/${applicationId}/documents`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
