import { useMemo } from 'react';
import { AlertTriangle, AlertCircle, Info, CheckCircle, FileText } from 'lucide-react';
import type { RiskFlag, RiskLevel } from '../../types';
import { getRiskColor, classNames } from '../../lib/utils';

interface FlagCardProps {
  flag: RiskFlag;
}

function formatDetails(text: string): string {
  if (!text) return '';
  const trimmed = text.trim();
  if (trimmed.startsWith('{')) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed.evidence) return String(parsed.evidence);
      if (parsed.field) return `Discrepancy identified in ${String(parsed.field).replace(/_/g, ' ')}.`;
      if (parsed.points !== undefined) return `Assessment rule applied (${parsed.points} risk penalty points).`;
    } catch {}
  }
  return text;
}

export function FlagCard({ flag }: FlagCardProps) {
  const colors = getRiskColor(flag.severity);

  const icons: Record<RiskLevel, React.ReactNode> = {
    HIGH: <AlertCircle className="h-4 w-4" />,
    MEDIUM: <AlertTriangle className="h-4 w-4" />,
    LOW: <Info className="h-4 w-4" />,
    PASS: <CheckCircle className="h-4 w-4" />,
  };

  const cleanDetails = formatDetails(flag.details);

  return (
    <div
      className={classNames('rounded-xl overflow-hidden border transition-all', colors.border)}
      style={{ background: '#141414' }}
    >
      {/* Header */}
      <div className={classNames('px-4 py-2.5 flex items-center justify-between', colors.bg)}>
        <div className="flex items-center gap-2">
          <span className={colors.text}>{icons[flag.severity]}</span>
          <span className={classNames('text-xs font-semibold uppercase tracking-wider', colors.text)}>
            {flag.severity} Priority
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="px-4 py-4 space-y-3">
        <h4 className="text-sm font-semibold" style={{ color: '#F0F0F0' }}>{flag.reason}</h4>
        {cleanDetails && (
          <p className="text-xs leading-relaxed" style={{ color: '#999999' }}>{cleanDetails}</p>
        )}

        {/* Evidence */}
        {flag.evidence.length > 0 && (
          <div className="space-y-1.5 pt-1">
            <p className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: '#666666' }}>Document Evidence</p>
            {flag.evidence.map((ev, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 rounded-lg px-3 py-2.5"
                style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.06)',
                }}
              >
                <FileText className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" style={{ color: '#AAFF00' }} strokeWidth={1.8} />
                <div className="text-xs min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="font-semibold" style={{ color: '#F0F0F0' }}>{ev.document}</span>
                    <span className="text-[11px] px-1.5 py-0.2 rounded" style={{ background: '#222222', color: '#888888' }}>
                      Page {ev.page || 1}
                    </span>
                  </div>
                  {ev.value && ev.value !== flag.reason && (
                    <p className="mt-1 text-[11px] leading-relaxed" style={{ color: '#AAAAAA' }}>{ev.value}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface FlagsSectionProps {
  flags: RiskFlag[];
}

export function FlagsSection({ flags }: FlagsSectionProps) {
  if (flags.length === 0) {
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
          <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Risk & Flags</h3>
        </div>
        <div className="py-8 text-center text-sm" style={{ color: '#666666' }}>
          No risk flags detected.
        </div>
      </div>
    );
  }

  // Deduplicate and sort: HIGH first, then MEDIUM, LOW, PASS
  const sorted = useMemo(() => {
    const seen = new Set<string>();
    const unique = flags.filter(f => {
      const key = (f.reason || '').trim().toLowerCase();
      if (!key) return true;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    const order: Record<RiskLevel, number> = { HIGH: 0, MEDIUM: 1, LOW: 2, PASS: 3 };
    return unique.sort((a, b) => order[a.severity] - order[b.severity]);
  }, [flags]);

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
          <h3 className="text-base font-semibold" style={{ color: '#F0F0F0' }}>Risk & Flags</h3>
          <p className="text-xs mt-0.5" style={{ color: '#666666' }}>{sorted.length} issue(s) detected</p>
        </div>
      </div>
      <div className="p-6 space-y-3">
        {sorted.map((flag) => (
          <FlagCard key={flag.id} flag={flag} />
        ))}
      </div>
    </div>
  );
}
