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
          <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Cross-Document Comparison</h3>
        </div>
        <div className="py-8 text-center text-sm" style={{ color: '#666666' }}>
          No comparison data available yet.
        </div>
      </div>
    );
  }

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
          <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Cross-Document Comparison</h3>
          <p className="text-xs mt-0.5" style={{ color: '#666666' }}>Values compared across submitted documents</p>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <th className="text-left py-3 px-6 font-semibold text-xs uppercase tracking-wider min-w-[120px]" style={{ color: '#555555' }}>Field</th>
              {docs.map(doc => (
                <th key={doc} className="text-left py-3 px-6 font-semibold text-xs uppercase tracking-wider min-w-[140px]" style={{ color: '#555555' }}>{doc}</th>
              ))}
              <th className="text-center py-3 px-6 font-semibold text-xs uppercase tracking-wider min-w-[100px]" style={{ color: '#555555' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {allFields.map((field, idx) => {
              const colors = getComparisonColor(field.status);
              return (
                <tr
                  key={`${field.field_name}-${idx}`}
                  className="transition-colors hover:bg-white/[0.02]"
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                >
                  <td className="py-3.5 px-6 font-medium" style={{ color: '#F0F0F0' }}>{field.field_name}</td>
                  {docs.map(doc => {
                    const match = field.values.find(v => v.document === doc);
                    return (
                      <td key={doc} className="py-3.5 px-6" style={{ color: '#A0A0A0' }}>
                        {match ? match.value : <span style={{ color: '#444444' }}>—</span>}
                      </td>
                    );
                  })}
                  <td className="py-3.5 px-6 text-center">
                    <span
                      className={classNames(
                        'inline-flex items-center px-2.5 py-0.5 text-xs font-semibold rounded-full border',
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
