/** FieldTable — Extracted fields with confidence bars."""
import { formatConfidence } from '../../utils/formatters';

export default function FieldTable({ fields, documentId }) {
  if (!fields) return <p>No extracted fields yet.</p>;

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b">
          <th className="text-left py-2">Field</th>
          <th className="text-left py-2">Value</th>
          <th className="text-left py-2">Confidence</th>
          <th className="text-left py-2">Source</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(fields).map(([key, field]) => (
          <tr key={key} className="border-b">
            <td className="py-2 font-medium">{key}</td>
            <td className="py-2">{String(field.value)}</td>
            <td className="py-2">{formatConfidence(field.confidence)}</td>
            <td className="py-2 text-gray-500">{documentId} p.{field.page}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
