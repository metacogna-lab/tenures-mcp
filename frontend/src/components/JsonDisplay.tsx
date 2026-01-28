interface JsonDisplayProps {
  data: unknown;
  title?: string;
}

export function JsonDisplay({ data, title }: JsonDisplayProps) {
  const formatted = JSON.stringify(data, null, 2);
  
  return (
    <div className="bg-bg-secondary rounded-lg border border-border-subtle overflow-hidden">
      {title && (
        <div className="px-4 py-2 border-b border-border-subtle bg-bg-tertiary">
          <span className="text-sm font-medium text-text-secondary">{title}</span>
        </div>
      )}
      <pre className="p-4 text-sm font-mono text-text-primary overflow-x-auto max-h-96 overflow-y-auto">
        <code>{formatted}</code>
      </pre>
    </div>
  );
}
