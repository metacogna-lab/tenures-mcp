interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'textarea';
  disabled?: boolean;
}

export function InputField({ 
  label, 
  value, 
  onChange, 
  placeholder, 
  type = 'text',
  disabled 
}: InputFieldProps) {
  const baseClasses = `
    w-full px-4 py-3 
    bg-bg-secondary border border-border-subtle 
    rounded-lg text-text-primary placeholder-text-muted
    focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent
    transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
  `;

  if (type === 'textarea') {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-text-secondary">{label}</label>
        <textarea
          className={`${baseClasses} min-h-[100px] resize-y font-mono text-sm`}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
        />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-text-secondary">{label}</label>
      <input
        type="text"
        className={baseClasses}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
      />
    </div>
  );
}
