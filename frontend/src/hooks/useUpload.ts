import { useState, useCallback } from 'react';
import { uploadDocuments } from '../api/documents';

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'failed';
}

export function useUpload(applicationId: string) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addFiles = useCallback((newFiles: File[]) => {
    const uploadFiles: UploadFile[] = newFiles.map(file => ({
      file,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      status: 'pending',
    }));
    setFiles(prev => [...prev, ...uploadFiles]);
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  }, []);

  const upload = useCallback(async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);
    setFiles(prev => prev.map(f => ({ ...f, status: 'uploading' })));

    try {
      const rawFiles = files.map(f => f.file);
      const results = await uploadDocuments(applicationId, rawFiles);

      setFiles(prev =>
        prev.map((f, i) => ({
          ...f,
          status: results[i]?.status === 'uploaded' ? 'uploaded' : 'failed',
        }))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setFiles(prev => prev.map(f => ({ ...f, status: 'failed' })));
    } finally {
      setUploading(false);
    }
  }, [applicationId, files]);

  const clearFiles = useCallback(() => {
    setFiles([]);
    setError(null);
  }, []);

  return { files, uploading, error, addFiles, removeFile, upload, clearFiles };
}
