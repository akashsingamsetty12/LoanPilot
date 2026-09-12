import { FileText, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { Card } from '../ui/Card';
import type { DashboardStats, Application } from '../../types';

interface SummaryCardsProps {
  stats?: DashboardStats;
  applications?: Application[];
}

export function SummaryCards({ stats, applications }: SummaryCardsProps) {
  const computedStats: DashboardStats = stats || {
    total: applications?.length || 0,
    pending: applications?.filter((a) => a.status === 'processing' || a.status === 'uploading').length || 0,
    needs_attention: applications?.filter((a) => a.status === 'review' || a.risk.level === 'HIGH' || a.risk.level === 'MEDIUM').length || 0,
    completed: applications?.filter((a) => a.status === 'completed').length || 0,
  };

  const cards = [
    {
      label: 'Total Applications',
      value: computedStats.total,
      icon: FileText,
      iconColor: 'text-primary-600',
      iconBg: 'bg-primary-50',
    },
    {
      label: 'Processing',
      value: computedStats.pending,
      icon: Clock,
      iconColor: 'text-primary-600',
      iconBg: 'bg-primary-50',
    },
    {
      label: 'Needs Attention',
      value: computedStats.needs_attention,
      icon: AlertTriangle,
      iconColor: 'text-risk-medium',
      iconBg: 'bg-amber-50',
    },
    {
      label: 'Completed',
      value: computedStats.completed,
      icon: CheckCircle,
      iconColor: 'text-risk-low',
      iconBg: 'bg-emerald-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.label} padding="md">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium text-charcoal-muted uppercase tracking-wider">{card.label}</p>
              <p className="text-2xl font-bold text-charcoal mt-1 tabular-nums">{card.value}</p>
            </div>
            <div className={`w-9 h-9 rounded-lg ${card.iconBg} flex items-center justify-center`}>
              <card.icon className={`h-[18px] w-[18px] ${card.iconColor}`} strokeWidth={1.8} />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
