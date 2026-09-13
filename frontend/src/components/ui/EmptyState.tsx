import { Inbox } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  message?: string;
  action?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  icon,
  title,
  description,
  message,
  action,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  const textMessage = message || description;

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-charcoal-muted mb-3">
        {icon || <Inbox className="h-10 w-10 mx-auto" strokeWidth={1.5} />}
      </div>
      <h3 className="text-base font-medium text-charcoal mb-1">{title}</h3>
      {textMessage && <p className="text-sm text-charcoal-muted max-w-sm">{textMessage}</p>}
      {action ? (
        <div className="mt-4">{action}</div>
      ) : actionLabel && onAction ? (
        <div className="mt-4">
          <Button onClick={onAction} size="sm">
            {actionLabel}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
