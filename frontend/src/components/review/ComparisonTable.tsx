import type { ComparisonField } from '../../types';
import { getComparisonColor, classNames } from '../../lib/utils';

interface ComparisonTableProps {
  matches: ComparisonField[];
  mismatches: ComparisonField[];
}

export function ComparisonTable({ matches, mismatches }: ComparisonTableProps) {
  const allFields = [...mismatches, ...matches];

  // Collect all unique document names
  const documentNames = new Set<string>();
  allFields.forEach(f => f.values.forEach(v => documentNames.add(v.document)));
  const docs = Array.from(documentNames);

  if (allFields.length === 0) {
    return (
      <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
        <div className="px-5 py-4 border-b border-surface-300">
          <h3 className="text-base font-semibold text-charcoal">Cross-Document Comparison</h3>
        </div>
        <div className="py-8 text-center text-sm text-charcoal-muted">
          No comparison data available yet.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
      <div className="px-5 py-4 border-b border-surface-300">
        <h3 className="text-base font-semibold text-charcoal">Cross-Document Comparison</h3>
        <p className="text-xs text-charcoal-muted mt-0.5">Values compared across submitted documents</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-50 border-b border-surface-200">
              <th className="text-left py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider min-w-[120px]">Field</th>
              {docs.map(doc => (
                <th key={doc} className="text-left py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider min-w-[140px]">{doc}</th>
              ))}
              <th className="text-center py-2.5 px-5 font-medium text-charcoal-muted text-xs uppercase tracking-wider min-w-[100px]">Status</th>
            </tr>
          </thead>
          <tbody>
            {allFields.map((field, idx) => {
              const colors = getComparisonColor(field.status);
              return (
                <tr key={`${field.field_name}-${idx}`} className="border-b border-surface-200 last:border-0">
                  <td className="py-3 px-5 font-medium text-charcoal">{field.field_name}</td>
                  {docs.map(doc => {
                    const match = field.values.find(v => v.document === doc);
                    return (
                      <td key={doc} className="py-3 px-5 text-charcoal-secondary">
                        {match ? match.value : <span className="text-charcoal-muted">—</span>}
                      </td>
                    );
                  })}
                  <td className="py-3 px-5 text-center">
                    <span
                      className={classNames(
                        'inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded border',
                        colors.text,
                        colors.bg,
                        colors.border
                      )}
                    >
                      {field.status}
                    </span>
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
