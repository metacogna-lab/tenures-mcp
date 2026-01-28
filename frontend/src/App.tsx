import { useState, useEffect } from 'react';
import { Badge } from './components/Badge';
import { Card } from './components/Card';
import { Button } from './components/Button';
import { InputField } from './components/InputField';
import { JsonDisplay } from './components/JsonDisplay';
import { StatusIndicator } from './components/StatusIndicator';
import { TestingGuide, type Scenario } from './components/TestingGuide';
import { useMcpApi } from './hooks/useMcpApi';
import type { Tool, Workflow, Resource } from './types';

// Realistic mock data with Ray White context
const TOOLS: Tool[] = [
  {
    id: 'analyze_open_home_feedback',
    name: 'Feedback Analysis',
    description: 'Sentiment analysis and categorization of open home visitor feedback from VaultRE',
    tier: 'A',
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
  {
    id: 'calculate_breach_status',
    name: 'Breach Detection',
    description: 'Arrears detection and breach risk classification for tenancies via Ailo',
    tier: 'A',
    inputSchema: { field: 'tenancy_id', type: 'text', placeholder: 'tenancy_001' },
  },
  {
    id: 'ocr_document',
    name: 'Document OCR',
    description: 'Text extraction from property management documents (certificates, contracts)',
    tier: 'A',
    inputSchema: { field: 'document_url', type: 'text', placeholder: 'https://vault.example.com/doc.pdf' },
  },
  {
    id: 'extract_expiry_date',
    name: 'Expiry Extraction',
    description: 'Parse expiry and compliance dates from extracted document text',
    tier: 'A',
    inputSchema: { field: 'text', type: 'text', placeholder: 'Certificate valid until 15/03/2026...' },
  },
  {
    id: 'generate_vendor_report',
    name: 'Vendor Reports',
    description: 'Weekly vendor report generation with market insights and comparable sales',
    tier: 'B',
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
  {
    id: 'prepare_breach_notice',
    name: 'Breach Notice',
    description: 'Draft breach notice generation with mandatory human-in-the-loop approval',
    tier: 'C',
    requiresHitl: true,
    inputSchema: { field: 'tenancy_id', type: 'text', placeholder: 'tenancy_001' },
  },
];

const WORKFLOWS: Workflow[] = [
  {
    id: 'weekly_vendor_report',
    name: 'Weekly Vendor Report',
    description: 'Complete vendor report generation with property details, feedback analysis, and market trends',
    steps: ['Fetch Property', 'Analyze Feedback', 'Get Market Data', 'Generate Report'],
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
  {
    id: 'arrears_detection',
    name: 'Arrears Detection',
    description: 'Tenant arrears analysis with breach risk classification and recommended actions',
    steps: ['Fetch Ledger', 'Calculate Breach', 'Classify Risk', 'Recommend Action'],
    inputSchema: { field: 'tenancy_id', type: 'text', placeholder: 'tenancy_001' },
  },
  {
    id: 'compliance_audit',
    name: 'Compliance Audit',
    description: 'Document compliance verification with OCR processing and expiry date extraction',
    steps: ['Fetch Documents', 'OCR Processing', 'Extract Dates', 'Validate Compliance'],
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
];

const RESOURCES: Resource[] = [
  {
    uri: 'vault://properties/{id}/details',
    name: 'Property Details',
    description: 'Property listing summary including address, price, and agent details',
    paramName: 'id',
    placeholder: 'prop_001',
  },
  {
    uri: 'vault://properties/{id}/feedback',
    name: 'Property Feedback',
    description: 'Open home visitor feedback entries with timestamps and comments',
    paramName: 'id',
    placeholder: 'prop_001',
  },
  {
    uri: 'ailo://ledgers/{tenancy_id}/summary',
    name: 'Ledger Summary',
    description: 'Tenancy ledger with balance, payment history, and arrears status',
    paramName: 'tenancy_id',
    placeholder: 'tenancy_001',
  },
  {
    uri: 'vault://properties/{id}/documents',
    name: 'Property Documents',
    description: 'Compliance documents, certificates, and contract URLs',
    paramName: 'id',
    placeholder: 'prop_001',
  },
];

type TabType = 'tools' | 'workflows' | 'resources' | 'guide';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('guide');
  const [selectedTool, setSelectedTool] = useState<Tool | null>(TOOLS[0]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(WORKFLOWS[0]);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(RESOURCES[0]);
  const [inputValue, setInputValue] = useState('');
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'loading'>('loading');

  const {
    toolState,
    workflowState,
    resourceState,
    healthState,
    readyState,
    checkHealth,
    checkReady,
    executeTool,
    executeWorkflow,
    fetchResource,
  } = useMcpApi();

  // Check server status on mount
  useEffect(() => {
    const checkServer = async () => {
      setServerStatus('loading');
      const health = await checkHealth();
      const ready = await checkReady();
      setServerStatus(health && ready ? 'online' : 'offline');
    };
    checkServer();
    const interval = setInterval(checkServer, 30000);
    return () => clearInterval(interval);
  }, [checkHealth, checkReady]);

  // Reset input when selection changes
  useEffect(() => {
    if (activeTab === 'tools' && selectedTool) {
      setInputValue(selectedTool.inputSchema.placeholder);
    } else if (activeTab === 'workflows' && selectedWorkflow) {
      setInputValue(selectedWorkflow.inputSchema.placeholder);
    } else if (activeTab === 'resources' && selectedResource) {
      setInputValue(selectedResource.placeholder);
    }
  }, [activeTab, selectedTool, selectedWorkflow, selectedResource]);

  const handleExecute = async () => {
    if (activeTab === 'tools' && selectedTool) {
      await executeTool(selectedTool.id, { [selectedTool.inputSchema.field]: inputValue });
    } else if (activeTab === 'workflows' && selectedWorkflow) {
      await executeWorkflow(selectedWorkflow.id, { [selectedWorkflow.inputSchema.field]: inputValue });
    } else if (activeTab === 'resources' && selectedResource) {
      const path = selectedResource.uri.replace(`{${selectedResource.paramName}}`, inputValue);
      await fetchResource(path);
    }
  };

  const handleSelectScenario = (scenario: Scenario) => {
    // Switch to workflows tab and set up the workflow
    const workflow = WORKFLOWS.find(w => w.id === scenario.workflow);
    if (workflow) {
      setActiveTab('workflows');
      setSelectedWorkflow(workflow);
      setInputValue(scenario.steps[0]?.input.value || '');
    }
  };

  const handleRunStep = (step: { input: { field: string; value: string } }) => {
    // Determine which tab based on input field
    const tool = TOOLS.find(t => t.inputSchema.field === step.input.field);
    if (tool) {
      setActiveTab('tools');
      setSelectedTool(tool);
      setInputValue(step.input.value);
    }
  };

  const isLoading = toolState.loading || workflowState.loading || resourceState.loading;
  const currentResult = activeTab === 'tools' 
    ? toolState.data 
    : activeTab === 'workflows' 
    ? workflowState.data 
    : activeTab === 'resources'
    ? resourceState.data
    : null;
  const currentError = activeTab === 'tools'
    ? toolState.error
    : activeTab === 'workflows'
    ? workflowState.error
    : activeTab === 'resources'
    ? resourceState.error
    : null;

  const tabConfig = [
    { id: 'guide' as const, label: 'Testing Guide', icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    )},
    { id: 'tools' as const, label: 'Tools', icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    )},
    { id: 'workflows' as const, label: 'Workflows', icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    )},
    { id: 'resources' as const, label: 'Resources', icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
    )},
  ];

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-border-subtle bg-bg-secondary/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center shadow-glow-sm">
                  <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-base font-semibold text-text-primary">Tenures MCP</h1>
                    <Badge variant="beta">Beta</Badge>
                  </div>
                  <p className="text-xs text-text-muted">Real Estate AI Platform</p>
                </div>
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center gap-4">
              <StatusIndicator 
                status={serverStatus} 
                label={serverStatus === 'online' ? 'Connected' : serverStatus === 'loading' ? 'Connecting...' : 'Disconnected'} 
              />
              {healthState.data && (
                <span className="text-xs text-text-muted font-mono px-2 py-1 bg-bg-tertiary rounded">
                  v{healthState.data.version}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* System Status */}
        {readyState.data && (
          <div className="mb-6 animate-fade-in-up">
            <Card variant="default" padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <span className="text-sm font-medium text-text-secondary">System Health</span>
                  <div className="flex items-center gap-4">
                    {[
                      { key: 'database', label: 'Database' },
                      { key: 'tools_registered', label: 'Tools' },
                      { key: 'resources_registered', label: 'Resources' },
                    ].map(({ key, label }) => (
                      <div key={key} className="flex items-center gap-2">
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          readyState.data?.checks[key as keyof typeof readyState.data.checks] 
                            ? 'bg-success' 
                            : 'bg-danger'
                        }`} />
                        <span className="text-sm text-text-secondary">{label}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <Badge 
                  variant={readyState.data.status === 'ready' ? 'success' : 'error'}
                  dot
                >
                  {readyState.data.status}
                </Badge>
              </div>
            </Card>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 mb-6 p-1 bg-bg-secondary rounded-xl border border-border-subtle">
          {tabConfig.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium 
                transition-all duration-150
                ${activeTab === tab.id
                  ? 'bg-bg-elevated text-text-primary shadow-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
                }
              `}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Testing Guide Tab */}
        {activeTab === 'guide' && (
          <div className="animate-fade-in-up">
            <TestingGuide 
              onSelectScenario={handleSelectScenario}
              onRunStep={handleRunStep}
            />
          </div>
        )}

        {/* Tools/Workflows/Resources Tabs */}
        {activeTab !== 'guide' && (
          <div className="grid grid-cols-12 gap-6 animate-fade-in-up">
            {/* Left Panel - Selection */}
            <div className="col-span-4 space-y-3">
              <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider px-1">
                Select {activeTab === 'tools' ? 'Tool' : activeTab === 'workflows' ? 'Workflow' : 'Resource'}
              </h2>
              
              {activeTab === 'tools' && TOOLS.map((tool, i) => (
                <Card 
                  key={tool.id} 
                  onClick={() => setSelectedTool(tool)}
                  selected={selectedTool?.id === tool.id}
                  className={`stagger-${i + 1}`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h3 className="font-medium text-text-primary">{tool.name}</h3>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <Badge variant={`tier-${tool.tier.toLowerCase()}` as 'tier-a' | 'tier-b' | 'tier-c'} size="sm">
                        Tier {tool.tier}
                      </Badge>
                      {tool.requiresHitl && <Badge variant="hitl" size="sm" dot>HITL</Badge>}
                    </div>
                  </div>
                  <p className="text-sm text-text-secondary leading-relaxed">{tool.description}</p>
                  <code className="text-xs text-text-muted font-mono mt-2 block">{tool.id}</code>
                </Card>
              ))}

              {activeTab === 'workflows' && WORKFLOWS.map((workflow, i) => (
                <Card 
                  key={workflow.id} 
                  onClick={() => setSelectedWorkflow(workflow)}
                  selected={selectedWorkflow?.id === workflow.id}
                  className={`stagger-${i + 1}`}
                >
                  <h3 className="font-medium text-text-primary mb-1">{workflow.name}</h3>
                  <p className="text-sm text-text-secondary mb-3">{workflow.description}</p>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {workflow.steps.map((step, idx) => (
                      <div key={idx} className="flex items-center gap-1">
                        <span className="text-xs bg-bg-secondary px-2 py-1 rounded text-text-muted">
                          {step}
                        </span>
                        {idx < workflow.steps.length - 1 && (
                          <svg className="w-3 h-3 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              ))}

              {activeTab === 'resources' && RESOURCES.map((resource, i) => (
                <Card 
                  key={resource.uri} 
                  onClick={() => setSelectedResource(resource)}
                  selected={selectedResource?.uri === resource.uri}
                  className={`stagger-${i + 1}`}
                >
                  <h3 className="font-medium text-text-primary mb-1">{resource.name}</h3>
                  <p className="text-sm text-text-secondary mb-2">{resource.description}</p>
                  <code className="text-xs text-accent-primary font-mono bg-accent-primary/10 px-2 py-1 rounded inline-block">
                    {resource.uri}
                  </code>
                </Card>
              ))}
            </div>

            {/* Right Panel - Execution */}
            <div className="col-span-8 space-y-6">
              {/* Input Section */}
              <Card variant="elevated">
                <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
                  Input Parameters
                </h2>
                <div className="space-y-4">
                  <InputField
                    label={
                      activeTab === 'tools' && selectedTool
                        ? selectedTool.inputSchema.field
                        : activeTab === 'workflows' && selectedWorkflow
                        ? selectedWorkflow.inputSchema.field
                        : selectedResource?.paramName || 'Input'
                    }
                    value={inputValue}
                    onChange={setInputValue}
                    placeholder={
                      activeTab === 'tools' && selectedTool
                        ? selectedTool.inputSchema.placeholder
                        : activeTab === 'workflows' && selectedWorkflow
                        ? selectedWorkflow.inputSchema.placeholder
                        : selectedResource?.placeholder
                    }
                    disabled={isLoading}
                    hint={
                      activeTab === 'tools' && selectedTool
                        ? `Tool: ${selectedTool.id}`
                        : activeTab === 'workflows' && selectedWorkflow
                        ? `Workflow: ${selectedWorkflow.id}`
                        : selectedResource
                        ? `URI: ${selectedResource.uri.replace(`{${selectedResource.paramName}}`, inputValue || '...')}`
                        : undefined
                    }
                  />
                  <div className="flex justify-end">
                    <Button
                      onClick={handleExecute}
                      loading={isLoading}
                      disabled={!inputValue || serverStatus !== 'online'}
                      icon={
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      }
                    >
                      {activeTab === 'resources' ? 'Fetch Resource' : 'Execute'}
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Result Section */}
              <div className="space-y-4">
                <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider px-1">
                  Response
                </h2>

                {currentError && (
                  <Card variant="default" className="border-danger/30 bg-danger/5 animate-fade-in-up">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-danger/20 flex items-center justify-center flex-shrink-0">
                        <svg className="w-4 h-4 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-danger">Error</h3>
                        <p className="text-sm text-text-secondary mt-1">{currentError}</p>
                      </div>
                    </div>
                  </Card>
                )}

                {currentResult && (
                  <div className="space-y-4 animate-fade-in-up">
                    {'success' in currentResult && (
                      <Card variant="default" className="border-success/30 bg-success/5">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-success/20 flex items-center justify-center">
                              <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                            <div>
                              <h3 className="font-medium text-success">Success</h3>
                              {'correlation_id' in currentResult && (
                                <p className="text-xs text-text-muted font-mono">
                                  {currentResult.correlation_id as string}
                                </p>
                              )}
                            </div>
                          </div>
                          {'execution_time_ms' in currentResult && typeof currentResult.execution_time_ms === 'number' && (
                            <span className="text-xs text-text-muted font-mono bg-bg-secondary px-2 py-1 rounded">
                              {currentResult.execution_time_ms.toFixed(1)}ms
                            </span>
                          )}
                        </div>
                      </Card>
                    )}
                    <JsonDisplay data={currentResult} title="Full Response" collapsible />
                  </div>
                )}

                {!currentResult && !currentError && !isLoading && (
                  <Card variant="outlined">
                    <div className="text-center py-12">
                      <div className="w-12 h-12 rounded-xl bg-bg-tertiary mx-auto mb-4 flex items-center justify-center">
                        <svg className="w-6 h-6 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <p className="text-text-muted">
                        Execute a {activeTab.slice(0, -1)} to see results
                      </p>
                      <p className="text-xs text-text-disabled mt-1">
                        Results will appear here with full JSON response
                      </p>
                    </div>
                  </Card>
                )}

                {isLoading && (
                  <Card variant="default" className="shimmer">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                        <svg className="w-4 h-4 text-accent-primary animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-text-primary">Processing...</h3>
                        <p className="text-xs text-text-muted">Executing request against MCP server</p>
                      </div>
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border-subtle mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-sm text-text-muted">
                Powered by <span className="text-text-secondary font-medium">Metacogna</span>
              </span>
              <div className="h-4 w-px bg-border-subtle" />
              <span className="text-xs text-text-muted">
                FastAPI + LangGraph + Pydantic
              </span>
            </div>
            <div className="flex items-center gap-4">
              <a 
                href="https://github.com/metacogna-lab/tenures-mcp" 
                className="text-sm text-text-muted hover:text-text-primary transition-colors flex items-center gap-1.5"
                target="_blank"
                rel="noopener noreferrer"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
                </svg>
                GitHub
              </a>
              <a 
                href="/api/docs" 
                className="text-sm text-text-muted hover:text-text-primary transition-colors"
              >
                API Docs
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
