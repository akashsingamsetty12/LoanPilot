import { AlertTriangle, Upload } from 'lucide-react';
import { Button } from '../ui/Button';

interface MissingDocumentsProps {
  documents: string[];
  onUpload?: () => void;
}

export function MissingDocuments({ documents, onUpload }: MissingDocumentsProps) {
  if (documents.length === 0) return null;

  return (
    <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
      <div className="px-5 py-4 border-b border-surface-300">
        <h3 className="text-base font-semibold text-charcoal">Missing Documents</h3>
        <p className="text-xs text-charcoal-muted mt-0.5">{documents.length} document(s) required</p>
      </div>
      <div className="p-5 space-y-2">
        {documents.map((doc) => (
          <div
            key={doc}
            className="flex items-center justify-between bg-risk-medium-bg border border-risk-medium-border rounded-md px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-4 w-4 text-risk-medium flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-charcoal">{doc}</p>
                <p className="text-xs text-charcoal-muted">Required for application verification</p>
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
