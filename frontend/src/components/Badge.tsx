interface BadgeProps {
  variant: 'beta' | 'tier-a' | 'tier-b' | 'tier-c' | 'hitl' | 'success' | 'error' | 'warning';
  children: React.ReactNode;
}

export function Badge({ variant, children }: BadgeProps) {
  const baseClasses = 'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider';
  
  const variantClasses = {
    'beta': 'bg-gradient-to-r from-amber-500 to-amber-600 text-black',
    'tier-a': 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    'tier-b': 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30',
    'tier-c': 'bg-red-500/20 text-red-400 border border-red-500/30',
    'hitl': 'bg-red-500/20 text-red-400 border border-red-500/30',
    'success': 'bg-emerald-500/20 text-emerald-400',
    'error': 'bg-red-500/20 text-red-400',
    'warning': 'bg-amber-500/20 text-amber-400',
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </span>
  );
}
