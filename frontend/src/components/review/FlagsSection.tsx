import { AlertTriangle, AlertCircle, Info, CheckCircle, FileText } from 'lucide-react';
import type { RiskFlag, RiskLevel } from '../../types';
import { getRiskColor, classNames } from '../../lib/utils';

interface FlagCardProps {
  flag: RiskFlag;
}

export function FlagCard({ flag }: FlagCardProps) {
  const colors = getRiskColor(flag.severity);

  const icons: Record<RiskLevel, React.ReactNode> = {
    HIGH: <AlertCircle className="h-4 w-4" />,
    MEDIUM: <AlertTriangle className="h-4 w-4" />,
    LOW: <Info className="h-4 w-4" />,
    PASS: <CheckCircle className="h-4 w-4" />,
  };

  return (
    <div
      className={classNames('rounded-lg overflow-hidden border', colors.border)}
      style={{ background: '#161616' }}
    >
      {/* Header */}
      <div className={classNames('px-4 py-2.5 flex items-center gap-2', colors.bg)}>
        <span className={colors.text}>{icons[flag.severity]}</span>
        <span className={classNames('text-xs font-semibold uppercase tracking-wider', colors.text)}>
          {flag.severity}
        </span>
      </div>

      {/* Body */}
      <div className="px-4 py-4 space-y-3">
        <h4 className="text-sm font-semibold" style={{ color: '#F0F0F0' }}>{flag.reason}</h4>
        <p className="text-sm leading-relaxed" style={{ color: '#A0A0A0' }}>{flag.details}</p>

        {/* Evidence */}
        {flag.evidence.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs font-medium uppercase tracking-wider" style={{ color: '#555555' }}>Evidence</p>
            {flag.evidence.map((ev, i) => (
              <div
                key={i}
                className="flex items-start gap-2 rounded px-3 py-2"
                style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid rgba(255,255,255,0.06)',
                }}
              >
                <FileText className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" style={{ color: '#666666' }} strokeWidth={1.5} />
                <div className="text-xs">
                  <span className="font-medium" style={{ color: '#F0F0F0' }}>{ev.document}</span>
                  <span style={{ color: '#666666' }}> · Page {ev.page}</span>
                  {ev.value && (
                    <p className="mt-0.5" style={{ color: '#888888' }}>{ev.value}</p>
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

  // Sort: HIGH first, then MEDIUM, LOW, PASS
  const order: Record<RiskLevel, number> = { HIGH: 0, MEDIUM: 1, LOW: 2, PASS: 3 };
  const sorted = [...flags].sort((a, b) => order[a.severity] - order[b.severity]);

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
          <p className="text-xs mt-0.5" style={{ color: '#666666' }}>{flags.length} issue(s) detected</p>
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
