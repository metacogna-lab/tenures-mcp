import { useState } from 'react';
import { Card } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';

interface Scenario {
  id: string;
  title: string;
  description: string;
  workflow: string;
  steps: {
    action: string;
    input: { field: string; value: string };
    expectedOutcome: string;
  }[];
  persona: string;
  tags: string[];
}

const SCENARIOS: Scenario[] = [
  {
    id: 'scenario-1',
    title: 'Weekly Vendor Report Generation',
    description: 'Generate a comprehensive weekly report for a property vendor, including market insights, open home feedback analysis, and comparable sales data.',
    workflow: 'weekly_vendor_report',
    persona: 'Sales Agent',
    tags: ['Sales', 'Reporting', 'High Priority'],
    steps: [
      {
        action: 'Fetch Property Details',
        input: { field: 'property_id', value: 'prop_001' },
        expectedOutcome: 'Property at 42 Harbour View, Manly NSW 2095 retrieved with listing price $2.8M',
      },
      {
        action: 'Analyze Open Home Feedback',
        input: { field: 'property_id', value: 'prop_001' },
        expectedOutcome: '15 feedback entries analyzed: 8 positive (53%), 5 neutral (33%), 2 negative (13%)',
      },
      {
        action: 'Generate Report',
        input: { field: 'property_id', value: 'prop_001' },
        expectedOutcome: 'PDF report generated with executive summary, feedback highlights, and recommended actions',
      },
    ],
  },
  {
    id: 'scenario-2',
    title: 'Tenant Arrears Detection & Breach Notice',
    description: 'Identify tenants in arrears, calculate breach status, and prepare breach notices for property managers.',
    workflow: 'arrears_detection',
    persona: 'Property Manager',
    tags: ['Property Management', 'Compliance', 'HITL Required'],
    steps: [
      {
        action: 'Fetch Ledger Summary',
        input: { field: 'tenancy_id', value: 'tenancy_001' },
        expectedOutcome: 'Ledger shows $3,200 outstanding balance, 14 days overdue',
      },
      {
        action: 'Calculate Breach Status',
        input: { field: 'tenancy_id', value: 'tenancy_001' },
        expectedOutcome: 'Breach risk: HIGH. Days overdue: 14. Recommended action: Issue breach notice',
      },
      {
        action: 'Prepare Breach Notice (HITL)',
        input: { field: 'tenancy_id', value: 'tenancy_001' },
        expectedOutcome: 'Draft breach notice generated, awaiting human approval before sending',
      },
    ],
  },
  {
    id: 'scenario-3',
    title: 'Compliance Document Audit',
    description: 'Audit property compliance documents, extract expiry dates, and flag any documents requiring renewal.',
    workflow: 'compliance_audit',
    persona: 'Compliance Officer',
    tags: ['Compliance', 'Document Processing', 'OCR'],
    steps: [
      {
        action: 'Fetch Property Documents',
        input: { field: 'property_id', value: 'prop_002' },
        expectedOutcome: '8 documents retrieved: smoke alarm cert, pool cert, electrical safety, etc.',
      },
      {
        action: 'OCR Document Processing',
        input: { field: 'document_url', value: 'https://vault.example.com/docs/smoke_alarm_cert.pdf' },
        expectedOutcome: 'Text extracted from smoke alarm compliance certificate',
      },
      {
        action: 'Extract Expiry Dates',
        input: { field: 'text', value: 'Certificate valid until 15/03/2026...' },
        expectedOutcome: 'Expiry date: 2026-03-15. Status: Valid (47 days remaining)',
      },
    ],
  },
  {
    id: 'scenario-4',
    title: 'Open Home Feedback Sentiment Analysis',
    description: 'Analyze visitor feedback from recent open homes to identify buyer sentiment and common objections.',
    workflow: 'N/A - Single Tool',
    persona: 'Sales Agent',
    tags: ['Sales', 'Analytics', 'Quick'],
    steps: [
      {
        action: 'Analyze Feedback',
        input: { field: 'property_id', value: 'prop_003' },
        expectedOutcome: `Sentiment breakdown:
- "Love the harbour views" → Positive (Location)
- "Kitchen needs updating" → Negative (Condition)  
- "Good sized bedrooms" → Positive (Layout)
- "Price seems high for area" → Negative (Price)`,
      },
    ],
  },
  {
    id: 'scenario-5',
    title: 'Multi-Property Portfolio Review',
    description: 'Generate reports for multiple properties in a vendor portfolio for quarterly review meeting.',
    workflow: 'weekly_vendor_report',
    persona: 'Senior Sales Agent',
    tags: ['Sales', 'Portfolio', 'Batch Processing'],
    steps: [
      {
        action: 'Process Property 1',
        input: { field: 'property_id', value: 'prop_001' },
        expectedOutcome: 'Report generated for 42 Harbour View, Manly',
      },
      {
        action: 'Process Property 2',
        input: { field: 'property_id', value: 'prop_004' },
        expectedOutcome: 'Report generated for 18 Beach Road, Bondi',
      },
      {
        action: 'Process Property 3',
        input: { field: 'property_id', value: 'prop_005' },
        expectedOutcome: 'Report generated for 7/120 Pacific Highway, Crows Nest',
      },
    ],
  },
];

interface TestingGuideProps {
  onSelectScenario: (scenario: Scenario) => void;
  onRunStep: (step: { action: string; input: { field: string; value: string } }) => void;
}

/**
 * Testing guide component with real estate scenarios.
 * Provides step-by-step guidance for testing MCP workflows.
 */
export function TestingGuide({ onSelectScenario, onRunStep }: TestingGuideProps) {
  const [expandedScenario, setExpandedScenario] = useState<string | null>(null);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  const toggleScenario = (id: string) => {
    setExpandedScenario(expandedScenario === id ? null : id);
  };

  const markStepComplete = (scenarioId: string, stepIndex: number) => {
    const key = `${scenarioId}-${stepIndex}`;
    const newCompleted = new Set(completedSteps);
    if (completedSteps.has(key)) {
      newCompleted.delete(key);
    } else {
      newCompleted.add(key);
    }
    setCompletedSteps(newCompleted);
  };

  const isStepComplete = (scenarioId: string, stepIndex: number) => {
    return completedSteps.has(`${scenarioId}-${stepIndex}`);
  };

  const getScenarioProgress = (scenario: Scenario) => {
    const completed = scenario.steps.filter((_, i) => 
      isStepComplete(scenario.id, i)
    ).length;
    return { completed, total: scenario.steps.length };
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">Testing Scenarios</h2>
          <p className="text-sm text-text-secondary mt-1">
            Real estate workflows to test the MCP server capabilities
          </p>
        </div>
        <Badge variant="info" size="md">
          {SCENARIOS.length} Scenarios
        </Badge>
      </div>

      <div className="space-y-3">
        {SCENARIOS.map((scenario) => {
          const isExpanded = expandedScenario === scenario.id;
          const progress = getScenarioProgress(scenario);
          const isComplete = progress.completed === progress.total;

          return (
            <Card 
              key={scenario.id} 
              variant="default"
              padding="none"
              className={isComplete ? 'border-success/30' : ''}
            >
              {/* Header */}
              <div 
                className="p-4 cursor-pointer"
                onClick={() => toggleScenario(scenario.id)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-text-primary truncate">
                        {scenario.title}
                      </h3>
                      {isComplete && (
                        <Badge variant="success" size="sm">Complete</Badge>
                      )}
                    </div>
                    <p className="text-sm text-text-secondary line-clamp-2">
                      {scenario.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2 flex-wrap">
                      <Badge variant="neutral" size="sm">{scenario.persona}</Badge>
                      {scenario.tags.slice(0, 2).map((tag) => (
                        <Badge 
                          key={tag} 
                          variant={tag.includes('HITL') ? 'hitl' : 'neutral'} 
                          size="sm"
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {/* Progress indicator */}
                    <div className="text-right">
                      <span className="text-sm font-medium text-text-primary">
                        {progress.completed}/{progress.total}
                      </span>
                      <div className="w-16 h-1 bg-bg-elevated rounded-full mt-1 overflow-hidden">
                        <div 
                          className="h-full bg-accent-primary transition-all duration-300"
                          style={{ width: `${(progress.completed / progress.total) * 100}%` }}
                        />
                      </div>
                    </div>
                    {/* Expand/collapse icon */}
                    <svg 
                      className={`w-5 h-5 text-text-muted transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Expanded content */}
              {isExpanded && (
                <div className="border-t border-border-subtle">
                  <div className="p-4 bg-bg-secondary/30">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-xs font-medium text-text-muted uppercase tracking-wider">
                        Workflow:
                      </span>
                      <code className="text-xs font-mono text-accent-primary bg-accent-primary/10 px-2 py-0.5 rounded">
                        {scenario.workflow}
                      </code>
                    </div>

                    {/* Steps */}
                    <div className="space-y-3">
                      {scenario.steps.map((step, index) => {
                        const stepComplete = isStepComplete(scenario.id, index);
                        
                        return (
                          <div 
                            key={index}
                            className={`
                              relative pl-8 py-3 px-4 rounded-lg border transition-all duration-200
                              ${stepComplete 
                                ? 'bg-success/5 border-success/20' 
                                : 'bg-bg-tertiary border-border-subtle hover:border-border-default'
                              }
                            `}
                          >
                            {/* Step number/check */}
                            <div 
                              className={`
                                absolute left-3 top-3.5 w-5 h-5 rounded-full flex items-center justify-center
                                text-xs font-medium cursor-pointer transition-all duration-200
                                ${stepComplete 
                                  ? 'bg-success text-white' 
                                  : 'bg-bg-elevated text-text-secondary border border-border-default'
                                }
                              `}
                              onClick={() => markStepComplete(scenario.id, index)}
                            >
                              {stepComplete ? (
                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                              ) : (
                                index + 1
                              )}
                            </div>

                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <h4 className={`font-medium ${stepComplete ? 'text-success' : 'text-text-primary'}`}>
                                  {step.action}
                                </h4>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => onRunStep(step)}
                                  icon={
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                  }
                                >
                                  Run
                                </Button>
                              </div>
                              
                              <div className="flex items-center gap-2 text-sm">
                                <span className="text-text-muted">Input:</span>
                                <code className="font-mono text-xs bg-bg-secondary px-2 py-0.5 rounded text-text-secondary">
                                  {step.input.field} = "{step.input.value}"
                                </code>
                              </div>

                              <div className="text-sm">
                                <span className="text-text-muted">Expected: </span>
                                <span className="text-text-secondary">{step.expectedOutcome}</span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Run All Button */}
                    <div className="mt-4 pt-4 border-t border-border-subtle flex justify-end">
                      <Button
                        variant="primary"
                        onClick={() => onSelectScenario(scenario)}
                        icon={
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                          </svg>
                        }
                      >
                        Run Full Workflow
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Quick Reference */}
      <Card variant="outlined" className="mt-8">
        <h3 className="text-sm font-semibold text-text-primary mb-3">Quick Reference: Test Data</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-text-muted">Properties:</span>
            <div className="mt-1 space-y-1 font-mono text-xs">
              <div className="text-text-secondary">prop_001 - 42 Harbour View, Manly</div>
              <div className="text-text-secondary">prop_002 - 15 Ocean Street, Bondi</div>
              <div className="text-text-secondary">prop_003 - 8/45 Pacific Hwy, Crows Nest</div>
            </div>
          </div>
          <div>
            <span className="text-text-muted">Tenancies:</span>
            <div className="mt-1 space-y-1 font-mono text-xs">
              <div className="text-text-secondary">tenancy_001 - In Arrears (14 days)</div>
              <div className="text-text-secondary">tenancy_002 - Current</div>
              <div className="text-text-secondary">tenancy_003 - In Arrears (7 days)</div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

export type { Scenario };
