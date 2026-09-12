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
    <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
      <div className="px-5 py-4 border-b border-surface-300">
        <h3 className="text-base font-semibold text-charcoal">Extracted Information</h3>
        <p className="text-xs text-charcoal-muted mt-0.5">Fields extracted from each document with source evidence</p>
      </div>
      <div className="divide-y divide-surface-200">
        {docsWithFields.length === 0 ? (
          <div className="py-8 text-center text-sm text-charcoal-muted">
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
        className="w-full flex items-center gap-3 px-5 py-3 hover:bg-surface-50 transition-colors text-left"
        aria-expanded={expanded}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4 text-charcoal-muted flex-shrink-0" />
        ) : (
          <ChevronRight className="h-4 w-4 text-charcoal-muted flex-shrink-0" />
        )}
        <FileText className="h-4 w-4 text-charcoal-muted flex-shrink-0" strokeWidth={1.5} />
        <span className="font-medium text-sm text-charcoal">{getDocumentTypeLabel(document.type)}</span>
        <span className="text-xs text-charcoal-muted">— {document.file_name}</span>
        <span className="ml-auto text-xs text-charcoal-muted tabular-nums">{document.fields.length} fields</span>
      </button>

      {expanded && (
        <div className="px-5 pb-4">
          <div className="bg-surface-50 rounded-md border border-surface-200 overflow-hidden">
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
    <div className={classNames('px-4 py-2.5', !isLast && 'border-b border-surface-200')}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-charcoal-muted">{field.field_name}</p>
          <p className="text-sm font-medium text-charcoal mt-0.5">{field.value}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <ConfidenceIndicator value={field.confidence} size="sm" />
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="p-1 rounded hover:bg-surface-200 text-charcoal-muted transition-colors"
            aria-label="Show evidence"
            title="View source"
          >
            <Info className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
      {showEvidence && (
        <div className="mt-2 flex items-center gap-2 text-xs text-charcoal-muted bg-white rounded px-3 py-1.5 border border-surface-200">
          <FileText className="h-3 w-3 flex-shrink-0" />
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
