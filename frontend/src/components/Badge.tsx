import { type ReactNode } from 'react';

type BadgeVariant = 
  | 'beta' 
  | 'tier-a' 
  | 'tier-b' 
  | 'tier-c' 
  | 'hitl' 
  | 'success' 
  | 'error' 
  | 'warning'
  | 'info'
  | 'neutral';

interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  size?: 'sm' | 'md';
  dot?: boolean;
  className?: string;
}

/**
 * Badge component for status indicators and labels.
 * Supports multiple variants for different semantic meanings.
 */
export function Badge({ variant, children, size = 'sm', dot, className = '' }: BadgeProps) {
  const baseClasses = `
    inline-flex items-center gap-1.5 font-semibold uppercase tracking-wider
    transition-colors duration-150
  `;
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px] rounded',
    md: 'px-2.5 py-1 text-xs rounded-md',
  };
  
  const variantClasses: Record<BadgeVariant, string> = {
    'beta': 'bg-gradient-to-r from-amber-500/90 to-amber-600/90 text-amber-950 shadow-sm',
    'tier-a': 'bg-success-muted text-success border border-success/20',
    'tier-b': 'bg-info-muted text-info border border-info/20',
    'tier-c': 'bg-danger-muted text-danger border border-danger/20',
    'hitl': 'bg-danger-muted text-danger border border-danger/20',
    'success': 'bg-success-muted text-success',
    'error': 'bg-danger-muted text-danger',
    'warning': 'bg-warning-muted text-warning',
    'info': 'bg-info-muted text-info',
    'neutral': 'bg-bg-elevated text-text-secondary border border-border-subtle',
  };

  const dotColors: Record<BadgeVariant, string> = {
    'beta': 'bg-amber-950',
    'tier-a': 'bg-success',
    'tier-b': 'bg-info',
    'tier-c': 'bg-danger',
    'hitl': 'bg-danger animate-pulse',
    'success': 'bg-success',
    'error': 'bg-danger',
    'warning': 'bg-warning',
    'info': 'bg-info',
    'neutral': 'bg-text-muted',
  };

  return (
    <span className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />}
      {children}
    </span>
  );
}
