import { useState, useEffect } from 'react';
import { Badge } from './components/Badge';
import { Card } from './components/Card';
import { Button } from './components/Button';
import { InputField } from './components/InputField';
import { JsonDisplay } from './components/JsonDisplay';
import { StatusIndicator } from './components/StatusIndicator';
import { useMcpApi } from './hooks/useMcpApi';
import type { Tool, Workflow, Resource } from './types';

// Realistic mock data
const TOOLS: Tool[] = [
  {
    id: 'analyze_open_home_feedback',
    name: 'Feedback Analysis',
    description: 'Sentiment analysis and categorization of open home visitor feedback',
    tier: 'A',
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
  {
    id: 'calculate_breach_status',
    name: 'Breach Detection',
    description: 'Arrears detection and breach risk classification for tenancies',
    tier: 'A',
    inputSchema: { field: 'tenancy_id', type: 'text', placeholder: 'tenancy_001' },
  },
  {
    id: 'ocr_document',
    name: 'Document OCR',
    description: 'Text extraction from property management documents',
    tier: 'A',
    inputSchema: { field: 'document_url', type: 'text', placeholder: 'https://example.com/doc.pdf' },
  },
  {
    id: 'extract_expiry_date',
    name: 'Expiry Extraction',
    description: 'Parse expiry and compliance dates from extracted text',
    tier: 'A',
    inputSchema: { field: 'text', type: 'text', placeholder: 'Contract expires on 15/01/2026...' },
  },
  {
    id: 'generate_vendor_report',
    name: 'Vendor Reports',
    description: 'Weekly vendor report generation with market insights',
    tier: 'B',
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
  {
    id: 'prepare_breach_notice',
    name: 'Breach Notice',
    description: 'Draft breach notice generation with HITL approval',
    tier: 'C',
    requiresHitl: true,
    inputSchema: { field: 'tenancy_id', type: 'text', placeholder: 'tenancy_001' },
  },
];

const WORKFLOWS: Workflow[] = [
  {
    id: 'weekly_vendor_report',
    name: 'Weekly Vendor Report',
    description: 'Complete vendor report generation workflow',
    steps: ['Fetch Property', 'Analyze Feedback', 'Get Market Data', 'Generate Report'],
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
  {
    id: 'arrears_detection',
    name: 'Arrears Detection',
    description: 'Tenant arrears analysis and risk classification',
    steps: ['Fetch Ledger', 'Calculate Breach', 'Classify Risk', 'Recommend Action'],
    inputSchema: { field: 'tenancy_id', type: 'text', placeholder: 'tenancy_001' },
  },
  {
    id: 'compliance_audit',
    name: 'Compliance Audit',
    description: 'Document compliance and expiry validation',
    steps: ['Fetch Documents', 'OCR Processing', 'Extract Dates', 'Validate Compliance'],
    inputSchema: { field: 'property_id', type: 'text', placeholder: 'prop_001' },
  },
];

const RESOURCES: Resource[] = [
  {
    uri: 'vault://properties/{id}/details',
    name: 'Property Details',
    description: 'Property listing summary from VaultRE',
    paramName: 'id',
    placeholder: 'prop_001',
  },
  {
    uri: 'vault://properties/{id}/feedback',
    name: 'Property Feedback',
    description: 'Open home feedback entries',
    paramName: 'id',
    placeholder: 'prop_001',
  },
  {
    uri: 'ailo://ledgers/{tenancy_id}/summary',
    name: 'Ledger Summary',
    description: 'Tenancy ledger balance and arrears',
    paramName: 'tenancy_id',
    placeholder: 'tenancy_001',
  },
  {
    uri: 'vault://properties/{id}/documents',
    name: 'Property Documents',
    description: 'Document URLs for contracts',
    paramName: 'id',
    placeholder: 'prop_001',
  },
];

type TabType = 'tools' | 'workflows' | 'resources';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('tools');
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

  const isLoading = toolState.loading || workflowState.loading || resourceState.loading;
  const currentResult = activeTab === 'tools' 
    ? toolState.data 
    : activeTab === 'workflows' 
    ? workflowState.data 
    : resourceState.data;
  const currentError = activeTab === 'tools'
    ? toolState.error
    : activeTab === 'workflows'
    ? workflowState.error
    : resourceState.error;

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-border-subtle bg-bg-secondary/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                    Tenures MCP
                    <Badge variant="beta">Beta</Badge>
                  </h1>
                  <p className="text-xs text-text-muted">Model Context Protocol Server</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <StatusIndicator 
                status={serverStatus} 
                label={serverStatus === 'online' ? 'Server Online' : serverStatus === 'loading' ? 'Connecting...' : 'Server Offline'} 
              />
              {healthState.data && (
                <span className="text-xs text-text-muted font-mono">v{healthState.data.version}</span>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Server Status Panel */}
        {readyState.data && (
          <div className="mb-8 animate-fade-in">
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-medium text-text-secondary mb-2">System Status</h2>
                  <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${readyState.data.checks.database ? 'bg-emerald-500' : 'bg-red-500'}`} />
                      <span className="text-sm text-text-primary">Database</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${readyState.data.checks.tools_registered ? 'bg-emerald-500' : 'bg-red-500'}`} />
                      <span className="text-sm text-text-primary">Tools Registered</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${readyState.data.checks.resources_registered ? 'bg-emerald-500' : 'bg-red-500'}`} />
                      <span className="text-sm text-text-primary">Resources Registered</span>
                    </div>
                  </div>
                </div>
                <Badge variant={readyState.data.status === 'ready' ? 'success' : 'error'}>
                  {readyState.data.status}
                </Badge>
              </div>
            </Card>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mb-6">
          {(['tools', 'workflows', 'resources'] as TabType[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab
                  ? 'bg-accent-primary text-white'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              <Badge variant="beta" className="ml-2 scale-75">Beta</Badge>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Selection */}
          <div className="col-span-4 space-y-4">
            <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider">
              Select {activeTab === 'tools' ? 'Tool' : activeTab === 'workflows' ? 'Workflow' : 'Resource'}
            </h2>
            
            {activeTab === 'tools' && TOOLS.map((tool) => (
              <Card 
                key={tool.id} 
                onClick={() => setSelectedTool(tool)}
                selected={selectedTool?.id === tool.id}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-text-primary">{tool.name}</h3>
                  <div className="flex items-center gap-2">
                    <Badge variant={`tier-${tool.tier.toLowerCase()}` as 'tier-a' | 'tier-b' | 'tier-c'}>
                      Tier {tool.tier}
                    </Badge>
                    {tool.requiresHitl && <Badge variant="hitl">HITL</Badge>}
                  </div>
                </div>
                <p className="text-sm text-text-secondary">{tool.description}</p>
                <p className="text-xs text-text-muted font-mono mt-2">{tool.id}</p>
              </Card>
            ))}

            {activeTab === 'workflows' && WORKFLOWS.map((workflow) => (
              <Card 
                key={workflow.id} 
                onClick={() => setSelectedWorkflow(workflow)}
                selected={selectedWorkflow?.id === workflow.id}
              >
                <h3 className="font-medium text-text-primary mb-2">{workflow.name}</h3>
                <p className="text-sm text-text-secondary mb-3">{workflow.description}</p>
                <div className="flex items-center gap-2 flex-wrap">
                  {workflow.steps.map((step, i) => (
                    <div key={i} className="flex items-center gap-1">
                      <span className="text-xs bg-bg-secondary px-2 py-1 rounded text-text-muted">{step}</span>
                      {i < workflow.steps.length - 1 && (
                        <span className="text-text-muted">→</span>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            ))}

            {activeTab === 'resources' && RESOURCES.map((resource) => (
              <Card 
                key={resource.uri} 
                onClick={() => setSelectedResource(resource)}
                selected={selectedResource?.uri === resource.uri}
              >
                <h3 className="font-medium text-text-primary mb-1">{resource.name}</h3>
                <p className="text-sm text-text-secondary mb-2">{resource.description}</p>
                <code className="text-xs text-accent-primary font-mono">{resource.uri}</code>
              </Card>
            ))}
          </div>

          {/* Right Panel - Execution */}
          <div className="col-span-8 space-y-6">
            {/* Input Section */}
            <Card>
              <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-4">
                Input
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
                />
                <div className="flex items-center justify-between">
                  <p className="text-xs text-text-muted">
                    {activeTab === 'tools' && selectedTool && (
                      <>Executing: <code className="text-accent-primary">{selectedTool.id}</code></>
                    )}
                    {activeTab === 'workflows' && selectedWorkflow && (
                      <>Workflow: <code className="text-accent-primary">{selectedWorkflow.id}</code></>
                    )}
                    {activeTab === 'resources' && selectedResource && (
                      <>Fetching: <code className="text-accent-primary">{selectedResource.uri.replace(`{${selectedResource.paramName}}`, inputValue || '...')}</code></>
                    )}
                  </p>
                  <Button
                    onClick={handleExecute}
                    loading={isLoading}
                    disabled={!inputValue || serverStatus !== 'online'}
                  >
                    {activeTab === 'resources' ? 'Fetch' : 'Execute'}
                  </Button>
                </div>
              </div>
            </Card>

            {/* Result Section */}
            <div className="space-y-4">
              <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider">
                Response
              </h2>

              {currentError && (
                <Card className="border-red-500/30 bg-red-500/5 animate-fade-in">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="font-medium text-red-400">Error</h3>
                      <p className="text-sm text-text-secondary mt-1">{currentError}</p>
                    </div>
                  </div>
                </Card>
              )}

              {currentResult && (
                <div className="animate-fade-in space-y-4">
                  {/* Summary Card */}
                  {'success' in currentResult && (
                    <Card className="border-emerald-500/30 bg-emerald-500/5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                          <div>
                            <h3 className="font-medium text-emerald-400">Success</h3>
                            <p className="text-xs text-text-muted font-mono">
                              {'correlation_id' in currentResult && currentResult.correlation_id}
                            </p>
                          </div>
                        </div>
                        {'execution_time_ms' in currentResult && currentResult.execution_time_ms && (
                          <span className="text-xs text-text-muted">
                            {(currentResult.execution_time_ms as number).toFixed(2)}ms
                          </span>
                        )}
                      </div>
                    </Card>
                  )}

                  {/* Full Response */}
                  <JsonDisplay data={currentResult} title="Full Response" />
                </div>
              )}

              {!currentResult && !currentError && !isLoading && (
                <Card className="border-dashed">
                  <div className="text-center py-8">
                    <div className="w-12 h-12 rounded-lg bg-bg-secondary mx-auto mb-4 flex items-center justify-center">
                      <svg className="w-6 h-6 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <p className="text-text-muted">Execute a {activeTab.slice(0, -1)} to see results</p>
                  </div>
                </Card>
              )}

              {isLoading && (
                <Card className="animate-pulse">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                      <svg className="w-4 h-4 text-accent-primary animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="font-medium text-text-primary">Processing...</h3>
                      <p className="text-xs text-text-muted">Executing request</p>
                    </div>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border-subtle mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-text-muted">
              <span>Powered by</span>
              <span className="text-text-secondary font-medium">Metacogna</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-text-muted">
              <a href="https://github.com/metacogna-lab/tenures-mcp" className="hover:text-text-primary transition-colors">
                GitHub
              </a>
              <a href="/api/docs" className="hover:text-text-primary transition-colors">
                API Docs
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
