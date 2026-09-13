import { useCallback, useRef, useState } from 'react';
import { Upload, X, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { formatFileSize, classNames } from '../../lib/utils';

interface UploadFile {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'failed';
}

interface DocumentUploadProps {
  files: UploadFile[];
  uploading: boolean;
  onAddFiles: (files: File[]) => void;
  onRemoveFile: (id: string) => void;
  onUpload: () => void;
}

const ACCEPTED_TYPES = ['application/pdf', 'image/jpeg', 'image/png'];

export function DocumentUpload({ files, uploading, onAddFiles, onRemoveFile, onUpload }: DocumentUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const droppedFiles = Array.from(e.dataTransfer.files).filter(f =>
        ACCEPTED_TYPES.includes(f.type)
      );
      if (droppedFiles.length > 0) onAddFiles(droppedFiles);
    },
    [onAddFiles]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = Array.from(e.target.files || []);
      if (selected.length > 0) onAddFiles(selected);
      if (inputRef.current) inputRef.current.value = '';
    },
    [onAddFiles]
  );

  const statusIcons = {
    pending: <FileText className="h-4 w-4 text-charcoal-muted" />,
    uploading: <Loader2 className="h-4 w-4 text-primary-600 animate-spin" />,
    uploaded: <CheckCircle className="h-4 w-4 text-risk-low" />,
    failed: <AlertCircle className="h-4 w-4 text-risk-high" />,
  };

  const statusLabels = {
    pending: 'Ready',
    uploading: 'Uploading…',
    uploaded: 'Uploaded',
    failed: 'Failed',
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={classNames(
          'border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-150',
          dragOver
            ? 'border-primary-400 bg-primary-50'
            : 'border-surface-300 hover:border-primary-300 hover:bg-surface-50'
        )}
      >
        <Upload className="h-8 w-8 text-charcoal-muted mx-auto mb-3" strokeWidth={1.5} />
        <p className="text-sm text-charcoal-secondary mb-1">
          Drag and drop files here, or{' '}
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="text-primary-600 font-medium hover:text-primary-700 underline-offset-2 hover:underline"
          >
            browse files
          </button>
        </p>
        <p className="text-xs text-charcoal-muted">PDF, JPG, PNG — up to 10MB each</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileSelect}
          className="hidden"
          aria-label="Upload documents"
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((f) => (
            <div
              key={f.id}
              className="flex items-center gap-3 bg-white border border-surface-300 rounded-md px-4 py-3"
            >
              {statusIcons[f.status]}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-charcoal truncate">{f.file.name}</p>
                <p className="text-xs text-charcoal-muted">{formatFileSize(f.file.size)}</p>
              </div>
              <span className="text-xs text-charcoal-muted">{statusLabels[f.status]}</span>
              {f.status === 'pending' && (
                <button
                  onClick={() => onRemoveFile(f.id)}
                  className="p-1 rounded hover:bg-surface-200 text-charcoal-muted transition-colors"
                  aria-label={`Remove ${f.file.name}`}
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload button */}
      {files.some(f => f.status === 'pending') && (
        <Button onClick={onUpload} loading={uploading} className="w-full">
          <Upload className="h-4 w-4" />
          Upload {files.filter(f => f.status === 'pending').length} Document(s)
        </Button>
      )}
    </div>
  );
}
