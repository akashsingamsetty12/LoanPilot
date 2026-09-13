import apiClient from './client';

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
    return files.map((file, i) => ({
      document_id: `DOC-MOCK-${Date.now()}-${i}`,
      file_name: file.name,
      status: 'uploaded' as const,
    }));
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
