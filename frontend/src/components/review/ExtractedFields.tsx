import { useState } from 'react';
import { ChevronDown, ChevronRight, FileText, Info } from 'lucide-react';
import type { LoanDocument, ExtractedField } from '../../types';
import { getDocumentTypeLabel, classNames } from '../../lib/utils';
import { ConfidenceIndicator } from '../ui/ConfidenceIndicator';

interface ExtractedFieldsProps {
  documents: LoanDocument[];
}

export function ExtractedFields({ documents }: ExtractedFieldsProps) {
  const docsWithFields = documents.filter(d => d.fields.length > 0);

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
          <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Extracted Information</h3>
          <p className="text-xs mt-0.5" style={{ color: '#666666' }}>Fields extracted from each document with source evidence</p>
        </div>
      </div>
      <div className="divide-y" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
        {docsWithFields.length === 0 ? (
          <div className="py-8 text-center text-sm" style={{ color: '#666666' }}>
            No extracted fields available yet.
          </div>
        ) : (
          docsWithFields.map((doc) => (
            <DocumentFieldGroup key={doc.document_id} document={doc} />
          ))
        )}
      </div>
    </div>
  );
}

function DocumentFieldGroup({ document }: { document: LoanDocument }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-6 py-3.5 transition-colors text-left hover:bg-white/[0.02]"
        aria-expanded={expanded}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4 flex-shrink-0" style={{ color: '#666666' }} />
        ) : (
          <ChevronRight className="h-4 w-4 flex-shrink-0" style={{ color: '#666666' }} />
        )}
        <FileText className="h-4 w-4 flex-shrink-0" style={{ color: '#666666' }} strokeWidth={1.5} />
        <span className="font-semibold text-sm" style={{ color: '#F0F0F0' }}>{getDocumentTypeLabel(document.type)}</span>
        <span className="text-xs" style={{ color: '#666666' }}>— {document.file_name}</span>
        <span className="ml-auto text-xs tabular-nums" style={{ color: '#666666' }}>{document.fields.length} fields</span>
      </button>

      {expanded && (
        <div className="px-6 pb-4">
          <div
            className="rounded-lg overflow-hidden"
            style={{
              background: '#161616',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            {document.fields.map((field, idx) => (
              <FieldRow
                key={`${field.field_name}-${idx}`}
                field={field}
                documentName={document.file_name}
                isLast={idx === document.fields.length - 1}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function FieldRow({
  field,
  documentName,
  isLast,
}: {
  field: ExtractedField;
  documentName: string;
  isLast: boolean;
}) {
  const [showEvidence, setShowEvidence] = useState(false);

  return (
    <div
      className={classNames('px-4 py-3', !isLast && 'border-b')}
      style={{ borderColor: 'rgba(255,255,255,0.04)' }}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-xs" style={{ color: '#666666' }}>{field.field_name}</p>
          <p className="text-sm font-medium mt-0.5" style={{ color: '#F0F0F0' }}>{field.value}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <ConfidenceIndicator value={field.confidence} size="sm" />
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="p-1 rounded transition-colors hover:bg-white/[0.06]"
            style={{ color: '#666666' }}
            aria-label="Show evidence"
            title="View source"
          >
            <Info className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
      {showEvidence && (
        <div
          className="mt-2.5 flex items-center gap-2 text-xs rounded px-3 py-1.5"
          style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.06)',
            color: '#888888',
          }}
        >
          <FileText className="h-3 w-3 flex-shrink-0" style={{ color: '#666666' }} />
          <span>Source: {documentName}</span>
          <span>·</span>
          <span>Page {field.page}</span>
          <span>·</span>
          <span>Confidence: {field.confidence}%</span>
        </div>
      )}
    </div>
  );
}
