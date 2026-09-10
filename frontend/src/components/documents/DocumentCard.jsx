/** DocumentCard — Single document display."""
import StatusBadge from '../application/StatusBadge';
import { DOC_TYPE_LABELS } from '../../utils/constants';
import { formatConfidence } from '../../utils/formatters';

export default function DocumentCard({ document }) {
  return (
    <div className="border rounded-lg p-4">
      <div className="flex justify-between items-start">
        <h4 className="font-medium">{document?.filename || 'Document'}</h4>
        <StatusBadge status={document?.status || 'uploaded'} />
      </div>
      <p className="text-sm text-gray-500 mt-1">
        Type: {DOC_TYPE_LABELS[document?.doc_type] || 'Unclassified'}
      </p>
      <p className="text-sm text-gray-500">
        Confidence: {formatConfidence(document?.ocr_confidence)}
      </p>
      {/* TODO: Add page count, extracted field count */}
    </div>
  );
}
