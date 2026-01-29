/**
 * Minimal landing page; function-first: single CTA to open the console.
 * Low information density; design tokens only.
 */

import { Link } from 'react-router-dom';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';

export function Landing() {
  return (
    <div className="min-h-screen bg-bg-primary flex flex-col">
      <header className="border-b border-border-subtle bg-bg-secondary/80 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-accent-primary flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-bg-primary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-text-primary text-lg">Tenures</span>
                  <Badge variant="beta" size="sm">
                    Beta
                  </Badge>
                </div>
                <span className="text-xs text-text-muted">Real estate agent console</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20">
        <div className="max-w-2xl w-full text-center space-y-8">
          <p className="text-sm text-text-muted label-uppercase tracking-wider">
            Realtor orchestration · Enterprise stack
          </p>
          <h1 className="text-4xl md:text-5xl font-bold text-text-primary leading-tight">
            <span className="text-text-primary">Agent workflows</span>
            <br />
            <span className="text-accent-primary">at your fingertips</span>
          </h1>
          <p className="text-lg text-text-secondary max-w-xl mx-auto">
            Run vendor reports, rental arrears checks, and breach notices. One click to the console.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Link to="/console">
              <Button variant="primary" size="lg" className="min-w-[200px]">
                Open Console
              </Button>
            </Link>
          </div>
        </div>
      </main>

      <footer className="border-t border-border-subtle py-4">
        <div className="max-w-4xl mx-auto px-6 text-center text-sm text-text-muted">
          Powered by Metacogna · MCP + LangGraph
        </div>
      </footer>
    </div>
  );
}
