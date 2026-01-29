interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'loading' | 'warning';
  label?: string;
  showPulse?: boolean;
}

/**
 * Status indicator with optional label.
 * Shows connection state with appropriate colors and animations.
 */
export function StatusIndicator({ status, label, showPulse = true }: StatusIndicatorProps) {
  const statusConfig = {
    online: {
      color: 'bg-accent-primary',
      ringColor: 'ring-accent-primary/30',
      label: label || 'Connected',
    },
    offline: {
      color: 'bg-danger',
      ringColor: 'ring-danger/30',
      label: label || 'Offline',
    },
    loading: {
      color: 'bg-warning',
      ringColor: 'ring-warning/30',
      label: label || 'Connecting...',
    },
    warning: {
      color: 'bg-warning',
      ringColor: 'ring-warning/30',
      label: label || 'Warning',
    },
  };

  const config = statusConfig[status];
  const shouldPulse = showPulse && (status === 'online' || status === 'loading');

  return (
    <div className="flex items-center gap-2">
      <span className="relative flex h-2 w-2">
        {shouldPulse && (
          <span 
            className={`
              absolute inline-flex h-full w-full rounded-full opacity-75 
              ${config.color} animate-ping
            `}
          />
        )}
        <span 
          className={`
            relative inline-flex rounded-full h-2 w-2 
            ${config.color}
            ${status === 'loading' ? 'animate-pulse' : ''}
          `}
        />
      </span>
      <span className="text-sm text-text-secondary">{config.label}</span>
    </div>
  );
}
