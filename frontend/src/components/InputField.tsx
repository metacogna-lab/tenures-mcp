import { type ChangeEvent, type ReactNode } from 'react';

interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'textarea';
  disabled?: boolean;
  error?: string;
  hint?: string;
  icon?: ReactNode;
  className?: string;
}

/**
 * Input field with label, hint, and error states.
 * Supports both single-line and multi-line input.
 */
export function InputField({ 
  label, 
  value, 
  onChange, 
  placeholder, 
  type = 'text',
  disabled,
  error,
  hint,
  icon,
  className = '',
}: InputFieldProps) {
  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const inputBaseClasses = `
    w-full px-4 py-3 
    bg-bg-secondary/80 
    border border-border-subtle 
    rounded-lg 
    text-text-primary placeholder-text-muted
    transition-all duration-150
    focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary/50
    disabled:opacity-50 disabled:cursor-not-allowed
    ${icon ? 'pl-11' : ''}
    ${error ? 'border-danger/50 focus:ring-danger/50 focus:border-danger/50' : ''}
  `;

  const InputWrapper = ({ children }: { children: ReactNode }) => (
    <div className={`space-y-2 ${className}`}>
      <label className="flex items-center justify-between">
        <span className="text-sm font-medium text-text-secondary">{label}</span>
        {hint && !error && (
          <span className="text-xs text-text-muted">{hint}</span>
        )}
        {error && (
          <span className="text-xs text-danger">{error}</span>
        )}
      </label>
      <div className="relative">
        {icon && (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted">
            {icon}
          </div>
        )}
        {children}
      </div>
    </div>
  );

  if (type === 'textarea') {
    return (
      <InputWrapper>
        <textarea
          className={`${inputBaseClasses} min-h-[120px] resize-y font-mono text-sm leading-relaxed`}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={disabled}
          rows={4}
        />
      </InputWrapper>
    );
  }

  return (
    <InputWrapper>
      <input
        type="text"
        className={inputBaseClasses}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
      />
    </InputWrapper>
  );
}
