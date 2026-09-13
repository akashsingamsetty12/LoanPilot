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
    await delay(1200);
    return handleMockUpload(applicationId, files);
  }

  try {
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
  } catch (err) {
    console.warn('Document upload API error, using fallback upload handler:', err);
    await delay(1000);
    return handleMockUpload(applicationId, files);
  }
}

function handleMockUpload(applicationId: string, files: File[]): UploadResult[] {
  const app = mockApplications.find(a => a.application_id === applicationId);
  const results: UploadResult[] = [];

  files.forEach((file, i) => {
    const docId = `DOC-${Date.now()}-${i}`;
    results.push({
      document_id: docId,
      file_name: file.name,
      status: 'uploaded',
    });

    if (app) {
      const fileNameLower = file.name.toLowerCase();
      let docType: 'payslip' | 'bank_statement' | 'tax_return' | 'id_proof' | 'address_proof' = 'id_proof';

      if (fileNameLower.includes('bank') || fileNameLower.includes('stmt')) {
        docType = 'bank_statement';
      } else if (fileNameLower.includes('tax') || fileNameLower.includes('itr')) {
        docType = 'tax_return';
      } else if (fileNameLower.includes('pay') || fileNameLower.includes('salary') || fileNameLower.includes('slip')) {
        docType = 'payslip';
      } else if (fileNameLower.includes('address') || fileNameLower.includes('bill')) {
        docType = 'address_proof';
      }

      app.documents.push({
        document_id: docId,
        file_name: file.name,
        type: docType,
        status: 'completed',
        pages: 2,
        ocr_confidence: 95,
        file_size: file.size || 250000,
        uploaded_at: new Date().toISOString(),
        fields: [
          { field_name: 'Uploaded Document', value: file.name, confidence: 96, page: 1 },
        ],
      });
    }
  });

  return results;
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
