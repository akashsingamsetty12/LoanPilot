import { FileText, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import type { DashboardStats, Application } from '../../types';

interface SummaryCardsProps {
  stats?: DashboardStats;
  applications?: Application[];
}

export function SummaryCards({ stats, applications }: SummaryCardsProps) {
  const computedStats: DashboardStats = stats || {
    total: applications?.length || 0,
    pending:
      applications?.filter(
        (a) => a.status === 'processing' || a.status === 'uploading'
      ).length || 0,
    needs_attention:
      applications?.filter(
        (a) =>
          a.status === 'review' ||
          a.risk.level === 'HIGH' ||
          a.risk.level === 'MEDIUM'
      ).length || 0,
    completed: applications?.filter((a) => a.status === 'completed').length || 0,
  };

  const cards = [
    {
      label: 'Total Applications',
      value: computedStats.total,
      icon: FileText,
      accentColor: '#AAFF00',
      bgColor: 'rgba(170,255,0,0.08)',
      borderColor: 'rgba(170,255,0,0.12)',
    },
    {
      label: 'Processing',
      value: computedStats.pending,
      icon: Clock,
      accentColor: '#60A5FA',
      bgColor: 'rgba(96,165,250,0.08)',
      borderColor: 'rgba(96,165,250,0.12)',
    },
    {
      label: 'Needs Attention',
      value: computedStats.needs_attention,
      icon: AlertTriangle,
      accentColor: '#FFB340',
      bgColor: 'rgba(255,179,64,0.08)',
      borderColor: 'rgba(255,179,64,0.12)',
    },
    {
      label: 'Completed',
      value: computedStats.completed,
      icon: CheckCircle,
      accentColor: '#30D158',
      bgColor: 'rgba(48,209,88,0.08)',
      borderColor: 'rgba(48,209,88,0.12)',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl p-5 transition-all duration-200 hover:-translate-y-0.5"
          style={{
            background: '#111111',
            border: '1px solid rgba(255,255,255,0.06)',
            boxShadow: '0 1px 3px rgba(0,0,0,0.5)',
          }}
        >
          <div className="flex items-start justify-between">
            <div>
              <p
                className="text-xs font-medium uppercase tracking-wider"
                style={{ color: '#555555' }}
              >
                {card.label}
              </p>
              <p
                className="text-3xl font-bold mt-2 tabular-nums"
                style={{ color: '#F0F0F0' }}
              >
                {card.value}
              </p>
            </div>
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{
                background: card.bgColor,
                border: `1px solid ${card.borderColor}`,
              }}
            >
              <card.icon
                style={{ width: 18, height: 18, color: card.accentColor }}
                strokeWidth={1.8}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
