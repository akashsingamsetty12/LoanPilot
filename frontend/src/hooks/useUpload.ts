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
    setFiles(prev => {
      const existingNames = new Set(prev.map(f => f.file.name));
      const uploadFiles: UploadFile[] = newFiles
        .filter(file => !existingNames.has(file.name))
        .map(file => ({
          file,
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          status: 'pending',
        }));
      return [...prev, ...uploadFiles];
    });
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  }, []);

  const upload = useCallback(async () => {
    const pendingFiles = files.filter(f => f.status === 'pending');
    if (pendingFiles.length === 0) return;

    setUploading(true);
    setError(null);
    setFiles(prev => prev.map(f => f.status === 'pending' ? { ...f, status: 'uploading' } : f));

    try {
      const rawFiles = pendingFiles.map(f => f.file);
      const results = await uploadDocuments(applicationId, rawFiles);

      setFiles(prev =>
        prev.map(f => {
          const matchedIdx = pendingFiles.findIndex(pf => pf.id === f.id);
          if (matchedIdx !== -1) {
            return {
              ...f,
              status: results[matchedIdx]?.status === 'uploaded' ? 'uploaded' : 'failed',
            };
          }
          return f;
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setFiles(prev => prev.map(f => f.status === 'uploading' ? { ...f, status: 'failed' } : f));
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
