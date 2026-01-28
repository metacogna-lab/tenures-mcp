interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'loading';
  label?: string;
}

export function StatusIndicator({ status, label }: StatusIndicatorProps) {
  const statusColors = {
    online: 'bg-emerald-500',
    offline: 'bg-red-500',
    loading: 'bg-amber-500 animate-pulse',
  };

  return (
    <div className="flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      {label && <span className="text-sm text-text-secondary">{label}</span>}
    </div>
  );
}
