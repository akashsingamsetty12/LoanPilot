/** VerificationTable — Cross-doc matches ✓ and mismatches ✗."""
export default function VerificationTable({ verification }) {
  if (!verification) return <p>No verification results yet.</p>;

  return (
    <div>
      {/* Matches */}
      <h3 className="font-medium text-green-700 mb-2">✓ Matches</h3>
      <ul className="mb-4">
        {(verification.matches || []).map((match, i) => (
          <li key={i} className="text-sm text-green-600">✓ {match}</li>
        ))}
      </ul>

      {/* Mismatches */}
      <h3 className="font-medium text-red-700 mb-2">✗ Mismatches</h3>
      {(verification.mismatches || []).map((mismatch, i) => (
        <div key={i} className="border border-red-200 rounded p-3 mb-2 bg-red-50">
          <p className="font-medium">{mismatch.field}</p>
          <p className="text-sm">Sources: {mismatch.sources?.join(' vs ')}</p>
          <p className="text-sm">Values: {mismatch.values?.join(' vs ')}</p>
          <p className="text-xs text-gray-500">Evidence: {mismatch.evidence}</p>
        </div>
      ))}

      {/* Missing Documents */}
      {verification.missing_documents?.length > 0 && (
        <>
          <h3 className="font-medium text-orange-700 mb-2">⚠ Missing Documents</h3>
          <ul>
            {verification.missing_documents.map((doc, i) => (
              <li key={i} className="text-sm text-orange-600">⚠ {doc}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
