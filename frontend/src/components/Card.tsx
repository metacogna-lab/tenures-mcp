import { type ReactNode, type MouseEvent } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: (e: MouseEvent<HTMLDivElement>) => void;
  selected?: boolean;
  variant?: 'default' | 'elevated' | 'outlined' | 'ghost';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

/**
 * Card component with multiple variants for different contexts.
 * Supports selection state for interactive lists.
 */
export function Card({ 
  children, 
  className = '', 
  onClick, 
  selected,
  variant = 'default',
  padding = 'md',
}: CardProps) {
  const baseClasses = `
    relative rounded-xl transition-all duration-200 ease-out
    inner-highlight
  `;
  
  const variantClasses = {
    default: `
      bg-bg-tertiary/80 border border-border-subtle
      ${onClick ? 'hover:bg-bg-elevated hover:border-border-default cursor-pointer' : ''}
    `,
    elevated: `
      bg-bg-elevated border border-border-default shadow-card
      ${onClick ? 'hover:shadow-card-hover hover:border-border-strong cursor-pointer' : ''}
    `,
    outlined: `
      bg-transparent border border-border-default border-dashed
      ${onClick ? 'hover:bg-bg-tertiary/50 hover:border-border-strong cursor-pointer' : ''}
    `,
    ghost: `
      bg-transparent border border-transparent
      ${onClick ? 'hover:bg-bg-tertiary cursor-pointer' : ''}
    `,
  };
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-6',
  };
  
  const selectedClasses = selected 
    ? 'border-accent-primary/50 bg-accent-primary/5 ring-1 ring-accent-primary/20' 
    : '';

  const interactiveClasses = onClick 
    ? 'active:scale-[0.98] hover:-translate-y-0.5' 
    : '';

  return (
    <div 
      className={`
        ${baseClasses} 
        ${variantClasses[variant]} 
        ${paddingClasses[padding]}
        ${selectedClasses} 
        ${interactiveClasses}
        ${className}
      `}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}
