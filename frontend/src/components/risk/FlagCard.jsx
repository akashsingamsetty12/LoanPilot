/** FlagCard — Risk flag with severity coloring and evidence."""
import { SEVERITY_CONFIG } from '../../utils/constants';

export default function FlagCard({ flag }) {
  const config = SEVERITY_CONFIG[flag?.severity] || SEVERITY_CONFIG.LOW;

  return (
    <div
      className="border rounded-lg p-4 mb-2"
      style={{ borderColor: config.border, backgroundColor: config.bg }}
    >
      <div className="flex items-center gap-2 mb-1">
        <span
          className="px-2 py-0.5 rounded text-xs font-bold text-white"
          style={{ backgroundColor: config.color }}
        >
          {flag?.severity}
        </span>
        <span className="text-sm font-medium">{flag?.reason}</span>
      </div>
      <p className="text-xs text-gray-500">Evidence: {flag?.evidence}</p>
    </div>
  );
}
