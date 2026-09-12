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
    <div className={classNames('border rounded-lg overflow-hidden', colors.border)}>
      {/* Header */}
      <div className={classNames('px-4 py-2.5 flex items-center gap-2', colors.bg)}>
        <span className={colors.text}>{icons[flag.severity]}</span>
        <span className={classNames('text-xs font-semibold uppercase tracking-wider', colors.text)}>
          {flag.severity}
        </span>
      </div>

      {/* Body */}
      <div className="bg-white px-4 py-4 space-y-3">
        <h4 className="text-sm font-semibold text-charcoal">{flag.reason}</h4>
        <p className="text-sm text-charcoal-secondary leading-relaxed">{flag.details}</p>

        {/* Evidence */}
        {flag.evidence.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-xs font-medium text-charcoal-muted uppercase tracking-wider">Evidence</p>
            {flag.evidence.map((ev, i) => (
              <div key={i} className="flex items-start gap-2 bg-surface-50 rounded px-3 py-2 border border-surface-200">
                <FileText className="h-3.5 w-3.5 text-charcoal-muted mt-0.5 flex-shrink-0" strokeWidth={1.5} />
                <div className="text-xs text-charcoal-secondary">
                  <span className="font-medium text-charcoal">{ev.document}</span>
                  <span className="text-charcoal-muted"> · Page {ev.page}</span>
                  {ev.value && (
                    <p className="text-charcoal-muted mt-0.5">{ev.value}</p>
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
      <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
        <div className="px-5 py-4 border-b border-surface-300">
          <h3 className="text-base font-semibold text-charcoal">Risk & Flags</h3>
        </div>
        <div className="py-8 text-center text-sm text-charcoal-muted">
          No risk flags detected.
        </div>
      </div>
    );
  }

  // Sort: HIGH first, then MEDIUM, LOW, PASS
  const order: Record<RiskLevel, number> = { HIGH: 0, MEDIUM: 1, LOW: 2, PASS: 3 };
  const sorted = [...flags].sort((a, b) => order[a.severity] - order[b.severity]);

  return (
    <div className="bg-white border border-surface-300 rounded-lg shadow-card overflow-hidden">
      <div className="px-5 py-4 border-b border-surface-300">
        <h3 className="text-base font-semibold text-charcoal">Risk & Flags</h3>
        <p className="text-xs text-charcoal-muted mt-0.5">{flags.length} issue(s) detected</p>
      </div>
      <div className="p-5 space-y-3">
        {sorted.map((flag) => (
          <FlagCard key={flag.id} flag={flag} />
        ))}
      </div>
    </div>
  );
}
