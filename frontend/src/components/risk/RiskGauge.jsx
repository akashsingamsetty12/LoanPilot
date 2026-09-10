/** RiskGauge — 0-100 risk score visualization."""
import { RISK_LEVELS } from '../../utils/constants';

export default function RiskGauge({ score, level }) {
  const config = RISK_LEVELS[level] || RISK_LEVELS.LOW;

  return (
    <div className="text-center">
      <div className="text-4xl font-bold" style={{ color: config.color }}>
        {score ?? '—'}
      </div>
      <div className="text-sm font-medium" style={{ color: config.color }}>
        {config.label}
      </div>
      {/* TODO: Add circular gauge visualization using recharts */}
    </div>
  );
}
