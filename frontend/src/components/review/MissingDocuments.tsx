import { AlertTriangle, Upload } from 'lucide-react';
import { Button } from '../ui/Button';

interface MissingDocumentsProps {
  documents: string[];
  onUpload?: () => void;
}

export function MissingDocuments({ documents, onUpload }: MissingDocumentsProps) {
  if (documents.length === 0) return null;

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{
        background: '#111111',
        border: '1px solid rgba(255,255,255,0.06)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.5)',
      }}
    >
      <div
        className="px-6 py-4"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
      >
        <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Missing Documents</h3>
        <p className="text-xs mt-0.5" style={{ color: '#666666' }}>{documents.length} document(s) required</p>
      </div>
      <div className="p-6 space-y-2">
        {documents.map((doc) => (
          <div
            key={doc}
            className="flex items-center justify-between rounded-lg px-4 py-3"
            style={{
              background: 'rgba(255,179,64,0.08)',
              border: '1px solid rgba(255,179,64,0.2)',
            }}
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-4 w-4 flex-shrink-0" style={{ color: '#FFB340' }} />
              <div>
                <p className="text-sm font-medium" style={{ color: '#F0F0F0' }}>{doc}</p>
                <p className="text-xs" style={{ color: '#888888' }}>Required for application verification</p>
              </div>
            </div>
            {onUpload && (
              <Button variant="secondary" size="sm" onClick={onUpload}>
                <Upload className="h-3.5 w-3.5" />
                Upload
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
