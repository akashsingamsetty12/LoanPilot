import { useMemo } from 'react';
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
  const uniqueDocuments = useMemo(() => {
    const seen = new Set<string>();
    return documents.filter((doc) => {
      const key = (doc.file_name || doc.document_id || '').toLowerCase();
      if (!key) return true;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [documents]);

  const statusStyles: Record<string, { label: string; dot: string }> = {
    completed: { label: 'Completed', dot: 'bg-risk-low' },
    processing: { label: 'Processing', dot: 'bg-primary-300 animate-pulse' },
    uploaded: { label: 'Uploaded', dot: 'bg-charcoal-muted' },
    failed: { label: 'Failed', dot: 'bg-risk-high' },
  };

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
        className="px-6 py-4 flex items-center justify-between"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
      >
        <div>
          <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Documents</h3>
          <p className="text-xs mt-0.5" style={{ color: '#666666' }}>{uniqueDocuments.length} document(s) submitted</p>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <th className="text-left py-3 px-6 font-semibold text-xs uppercase tracking-wider" style={{ color: '#555555' }}>Document</th>
              <th className="text-left py-3 px-6 font-semibold text-xs uppercase tracking-wider" style={{ color: '#555555' }}>Type</th>
              <th className="text-center py-3 px-6 font-semibold text-xs uppercase tracking-wider" style={{ color: '#555555' }}>Status</th>
              <th className="text-center py-3 px-6 font-semibold text-xs uppercase tracking-wider" style={{ color: '#555555' }}>Pages</th>
              <th className="text-center py-3 px-6 font-semibold text-xs uppercase tracking-wider" style={{ color: '#555555' }}>OCR Confidence</th>
              <th className="text-right py-3 px-6 font-semibold text-xs uppercase tracking-wider" style={{ color: '#555555' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {uniqueDocuments.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-sm" style={{ color: '#666666' }}>
                  No documents uploaded yet.
                </td>
              </tr>
            ) : (
              uniqueDocuments.map((doc) => {
                const st = statusStyles[doc.status] || statusStyles.uploaded;
                return (
                  <tr
                    key={doc.document_id}
                    className="transition-colors hover:bg-white/[0.02]"
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                  >
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-2.5">
                        <FileText className="h-4 w-4 flex-shrink-0" style={{ color: '#666666' }} strokeWidth={1.5} />
                        <span className="font-medium truncate max-w-[220px]" style={{ color: '#F0F0F0' }}>
                          {doc.file_name}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-6" style={{ color: '#A0A0A0' }}>
                      {getDocumentTypeLabel(doc.type)}
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="flex items-center justify-center gap-1.5">
                        <span className={classNames('w-1.5 h-1.5 rounded-full', st.dot)} />
                        <span style={{ color: '#A0A0A0' }}>{st.label}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-center tabular-nums" style={{ color: '#A0A0A0' }}>
                      {doc.pages}
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="flex justify-center">
                        {doc.ocr_confidence > 0 ? (
                          <ConfidenceIndicator value={doc.ocr_confidence} />
                        ) : (
                          <span className="text-xs" style={{ color: '#555555' }}>—</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-right">
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
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
