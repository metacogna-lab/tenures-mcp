import { useState } from 'react';
import { Button } from './Button';

interface JsonDisplayProps {
  data: unknown;
  title?: string;
  maxHeight?: string;
  collapsible?: boolean;
}

/**
 * JSON viewer with syntax highlighting and copy functionality.
 * Supports collapsible sections for large data.
 */
export function JsonDisplay({ 
  data, 
  title, 
  maxHeight = '400px',
  collapsible = false,
}: JsonDisplayProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const formatted = JSON.stringify(data, null, 2);
  
  const handleCopy = async () => {
    await navigator.clipboard.writeText(formatted);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Simple syntax highlighting
  const highlightJson = (json: string) => {
    return json
      .replace(/"([^"]+)":/g, '<span class="text-accent-tertiary">"$1"</span>:')
      .replace(/: "([^"]*)"/g, ': <span class="text-success">"$1"</span>')
      .replace(/: (true|false)/g, ': <span class="text-warning">$1</span>')
      .replace(/: (\d+\.?\d*)/g, ': <span class="text-info">$1</span>')
      .replace(/: (null)/g, ': <span class="text-text-muted">$1</span>');
  };
  
  return (
    <div className="bg-bg-secondary rounded-xl border border-border-subtle overflow-hidden">
      {title && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-bg-tertiary/50">
          <div className="flex items-center gap-3">
            {collapsible && (
              <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                <svg 
                  className={`w-4 h-4 transition-transform duration-200 ${isCollapsed ? '-rotate-90' : ''}`}
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            )}
            <span className="text-sm font-medium text-text-secondary">{title}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            icon={
              copied ? (
                <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )
            }
          >
            {copied ? 'Copied!' : 'Copy'}
          </Button>
        </div>
      )}
      {!isCollapsed && (
        <div 
          className="overflow-auto p-4"
          style={{ maxHeight }}
        >
          <pre className="text-sm font-mono text-text-primary leading-relaxed">
            <code dangerouslySetInnerHTML={{ __html: highlightJson(formatted) }} />
          </pre>
        </div>
      )}
    </div>
  );
}
