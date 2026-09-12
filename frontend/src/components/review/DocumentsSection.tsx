import { FileText, Eye } from 'lucide-react';
import type { LoanDocument } from '../../types';
import { getDocumentTypeLabel, classNames } from '../../lib/utils';
import { ConfidenceIndicator } from '../ui/ConfidenceIndicator';
import { Button } from '../ui/Button';

interface DocumentsSectionProps {
  documents: LoanDocument[];
  onViewDocument?: (docId: string) => void;
}

export function DocumentsSection({ documents, onViewDocument }: DocumentsSectionProps) {
  const statusStyles: Record<string, { label: string; dot: string }> = {
    completed: { label: 'Completed', dot: 'bg-risk-low' },
    processing: { label: 'Processing', dot: 'bg-primary-500 animate-pulse' },
    uploaded: { label: 'Uploaded', dot: 'bg-charcoal-muted' },
    failed: { label: 'Failed', dot: 'bg-risk-high' },
  };

  return (
    <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
      <div className="px-5 py-4 border-b border-surface-300">
        <h3 className="text-base font-semibold text-charcoal">Documents</h3>
        <p className="text-xs text-charcoal-muted mt-0.5">{documents.length} document(s) submitted</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-50 border-b border-surface-200">
              <th className="text-left py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Document</th>
              <th className="text-left py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Type</th>
              <th className="text-center py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Status</th>
              <th className="text-center py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Pages</th>
              <th className="text-center py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider">OCR Confidence</th>
              <th className="text-right py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => {
              const st = statusStyles[doc.status] || statusStyles.uploaded;
              return (
                <tr key={doc.document_id} className="border-b border-surface-200 last:border-0">
                  <td className="py-3 px-5">
                    <div className="flex items-center gap-2.5">
                      <FileText className="h-4 w-4 text-charcoal-muted flex-shrink-0" strokeWidth={1.5} />
                      <span className="font-medium text-charcoal truncate max-w-[200px]">{doc.file_name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-5 text-charcoal-secondary">{getDocumentTypeLabel(doc.type)}</td>
                  <td className="py-3 px-5">
                    <div className="flex items-center justify-center gap-1.5">
                      <span className={classNames('w-1.5 h-1.5 rounded-full', st.dot)} />
                      <span className="text-charcoal-secondary">{st.label}</span>
                    </div>
                  </td>
                  <td className="py-3 px-5 text-center text-charcoal-secondary tabular-nums">{doc.pages}</td>
                  <td className="py-3 px-5">
                    <div className="flex justify-center">
                      {doc.ocr_confidence > 0 ? (
                        <ConfidenceIndicator value={doc.ocr_confidence} />
                      ) : (
                        <span className="text-charcoal-muted text-xs">—</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-5 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewDocument?.(doc.document_id)}
                      aria-label={`View ${doc.file_name}`}
                    >
                      <Eye className="h-3.5 w-3.5" />
                      View
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
