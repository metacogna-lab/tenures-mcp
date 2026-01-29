import { type ReactNode, type ButtonHTMLAttributes } from 'react';

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  className?: string;
}

/**
 * Button component with consistent styling and loading states.
 * Supports multiple variants and sizes.
 */
export function Button({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md',
  disabled,
  loading,
  icon,
  iconPosition = 'left',
  fullWidth,
  className = '',
  ...props
}: ButtonProps) {
  const baseClasses = `
    relative inline-flex items-center justify-center gap-2
    font-medium rounded-lg
    transition-all duration-150 ease-out
    disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
    active:scale-[0.98]
  `;
  
  const variantClasses = {
    primary: `
      bg-accent-primary text-bg-primary
      hover:bg-accent-primary-hover
      shadow-glow-sm hover:shadow-glow
      focus-visible:ring-2 focus-visible:ring-accent-primary focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary
    `,
    secondary: `
      bg-bg-elevated border border-border-default text-text-primary
      hover:bg-bg-hover hover:border-border-strong
      focus-visible:ring-2 focus-visible:ring-border-strong focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary
    `,
    ghost: `
      bg-transparent text-text-secondary
      hover:text-text-primary hover:bg-bg-hover
      focus-visible:ring-2 focus-visible:ring-border-default focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary
    `,
    danger: `
      bg-danger/10 text-danger border border-danger/20
      hover:bg-danger/20 hover:border-danger/30
      focus-visible:ring-2 focus-visible:ring-danger focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary
    `,
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-5 py-3 text-base',
  };

  const LoadingSpinner = () => (
    <svg 
      className="animate-spin h-4 w-4" 
      fill="none" 
      viewBox="0 0 24 24"
    >
      <circle 
        className="opacity-25" 
        cx="12" cy="12" r="10" 
        stroke="currentColor" 
        strokeWidth="4" 
      />
      <path 
        className="opacity-75" 
        fill="currentColor" 
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" 
      />
    </svg>
  );

  return (
    <button
      className={`
        ${baseClasses} 
        ${variantClasses[variant]} 
        ${sizeClasses[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <LoadingSpinner />}
      {!loading && icon && iconPosition === 'left' && icon}
      <span className={loading ? 'opacity-0' : ''}>{children}</span>
      {loading && <span className="absolute">{children}</span>}
      {!loading && icon && iconPosition === 'right' && icon}
    </button>
  );
}
