interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  selected?: boolean;
}

export function Card({ children, className = '', onClick, selected }: CardProps) {
  const baseClasses = 'bg-bg-tertiary border border-border-subtle rounded-xl p-5 transition-all duration-200';
  const interactiveClasses = onClick ? 'cursor-pointer hover:bg-bg-hover hover:border-border-default hover:-translate-y-0.5' : '';
  const selectedClasses = selected ? 'border-accent-primary bg-bg-hover' : '';

  return (
    <div 
      className={`${baseClasses} ${interactiveClasses} ${selectedClasses} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
