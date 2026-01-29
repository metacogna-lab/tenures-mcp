/**
 * Console shell: flow cards, execution form with validation, result area, footer status.
 * Function-first primary work surface; Testing Guide and LangGraph Demo as tabs.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Badge } from '../components/Badge';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { InputField } from '../components/InputField';
import { JsonDisplay } from '../components/JsonDisplay';
import { StatusIndicator } from '../components/StatusIndicator';
import { TestingGuide, type Scenario } from '../components/TestingGuide';
import { LiveWorkflowReport } from '../components/LiveWorkflowReport';
import { useMcpApi } from '../hooks/useMcpApi';
import { FLOW_CONFIG, getFlowById, type FlowConfig } from '../data/flowConfig';
import { MOCK_FLOW_PREFILL } from '../data/mock';
import { validateToolInput, validateWorkflowInput } from '../lib/validation';

type TabType = 'flows' | 'guide' | 'langgraph';

const tabConfig = [
  {
    id: 'flows' as const,
    label: 'Flows',
    highlight: true,
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  {
    id: 'guide' as const,
    label: 'Testing Guide',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
  },
  {
    id: 'langgraph' as const,
    label: 'LangGraph Demo',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
    ),
  },
];

export function Console() {
  const { id: flowIdParam } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('flows');
  const [selectedFlow, setSelectedFlow] = useState<FlowConfig | null>(FLOW_CONFIG[0]);
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [hitlToken, setHitlToken] = useState('');
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'loading'>('loading');

  const {
    toolState,
    workflowState,
    healthState,
    readyState,
    checkHealth,
    checkReady,
    executeTool,
    executeWorkflow,
  } = useMcpApi();

  // Sync selected flow from route param
  useEffect(() => {
    if (flowIdParam) {
      const flow = getFlowById(flowIdParam);
      if (flow) {
        setSelectedFlow(flow);
        setFieldErrors({});
      }
    }
  }, [flowIdParam]);

  // Prefill form when selected flow changes
  useEffect(() => {
    if (selectedFlow) {
      const prefill = MOCK_FLOW_PREFILL[selectedFlow.id] ?? {};
      const initial: Record<string, string> = {};
      selectedFlow.inputFields.forEach((f) => {
        initial[f.name] = prefill[f.name] ?? f.placeholder;
      });
      setFormValues(initial);
    }
  }, [selectedFlow?.id]);

  // Server status
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

  const handleSelectFlow = (flow: FlowConfig) => {
    setSelectedFlow(flow);
    setFieldErrors({});
    navigate(`/console/flow/${flow.id}`);
    const prefill = MOCK_FLOW_PREFILL[flow.id] ?? {};
    const initial: Record<string, string> = {};
    flow.inputFields.forEach((f) => {
      initial[f.name] = prefill[f.name] ?? f.placeholder;
    });
    setFormValues(initial);
  };

  const handleSubmit = async () => {
    if (!selectedFlow) return;
    setFieldErrors({});

    const inputData: Record<string, unknown> = {};
    selectedFlow.inputFields.forEach((f) => {
      const v = formValues[f.name]?.trim();
      inputData[f.name] = v ?? '';
    });

    if (selectedFlow.type === 'tool') {
      const result = validateToolInput(selectedFlow.endpointId, inputData);
      if (!result.success) {
        const errors: Record<string, string> = {};
        result.errors.forEach((msg) => {
          const [field] = msg.split(':');
          errors[field?.trim() ?? ''] = msg;
        });
        setFieldErrors(errors);
        return;
      }
      await executeTool(selectedFlow.endpointId, result.data, selectedFlow.requiresHitl ? hitlToken : undefined);
    } else {
      const result = validateWorkflowInput(selectedFlow.endpointId, inputData);
      if (!result.success) {
        const errors: Record<string, string> = {};
        result.errors.forEach((msg) => {
          const [field] = msg.split(':');
          errors[field?.trim() ?? ''] = msg;
        });
        setFieldErrors(errors);
        return;
      }
      await executeWorkflow(selectedFlow.endpointId, result.data);
    }
  };

  const handleSelectScenario = (scenario: Scenario) => {
    const flow = FLOW_CONFIG.find((f) => f.endpointId === scenario.workflow);
    if (flow) {
      setActiveTab('flows');
      handleSelectFlow(flow);
      const firstValue = scenario.steps[0]?.input?.value;
      if (firstValue && flow.inputFields[0]) {
        setFormValues((prev) => ({ ...prev, [flow.inputFields[0].name]: firstValue }));
      }
    }
  };

  const handleRunStep = (_step: { input: { field: string; value: string } }) => {
    // Optional: focus flow form
  };

  const isLoading = toolState.loading || workflowState.loading;
  const currentResult = selectedFlow?.type === 'tool' ? toolState.data : workflowState.data;
  const currentError = selectedFlow?.type === 'tool' ? toolState.error : workflowState.error;

  return (
    <div className="min-h-screen bg-bg-primary flex flex-col">
      <header className="border-b border-border-subtle bg-bg-secondary/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
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
                  <p className="text-xs text-text-muted">Real Estate Agent Console</p>
                </div>
              </div>
            </div>
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

      <main className="max-w-7xl mx-auto px-6 py-8 flex-1">
        {readyState.data && (
          <div className="mb-6 animate-fade-in-up">
            <Card variant="default" padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <span className="text-sm font-medium text-text-secondary">System Health</span>
                  <div className="flex items-center gap-4">
                    {['database', 'tools_registered', 'resources_registered'].map((key, i) => (
                      <div key={key} className="flex items-center gap-2">
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            readyState.data?.checks[key as keyof typeof readyState.data.checks] ? 'bg-success' : 'bg-danger'
                          }`}
                        />
                        <span className="text-sm text-text-secondary">
                          {['Database', 'Tools', 'Resources'][i]}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <Badge variant={readyState.data.status === 'ready' ? 'success' : 'error'} dot>
                  {readyState.data.status}
                </Badge>
              </div>
            </Card>
          </div>
        )}

        <div className="flex items-center gap-1 mb-6 p-1 bg-bg-secondary rounded-xl border border-border-subtle">
          {tabConfig.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 relative
                ${activeTab === tab.id
                  ? tab.highlight
                    ? 'bg-gradient-to-r from-accent-primary to-accent-secondary text-white shadow-glow-sm'
                    : 'bg-bg-elevated text-text-primary shadow-sm'
                  : tab.highlight
                    ? 'text-accent-primary hover:text-accent-primary-hover hover:bg-accent-primary/10'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
                }
              `}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'guide' && (
          <div className="animate-fade-in-up">
            <TestingGuide onSelectScenario={handleSelectScenario} onRunStep={handleRunStep} />
          </div>
        )}

        {activeTab === 'langgraph' && (
          <div className="animate-fade-in-up">
            <LiveWorkflowReport />
          </div>
        )}

        {activeTab === 'flows' && (
          <div className="grid grid-cols-12 gap-6 animate-fade-in-up">
            <div className="col-span-4 space-y-3">
              <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider px-1 label-uppercase">
                Flows
              </h2>
              {FLOW_CONFIG.map((flow, i) => (
                <Card
                  key={flow.id}
                  onClick={() => handleSelectFlow(flow)}
                  selected={selectedFlow?.id === flow.id}
                  className={`stagger-${i + 1}`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h3 className="font-medium text-text-primary">{flow.name}</h3>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <Badge variant={flow.type === 'workflow' ? 'tier-b' : 'tier-a'} size="sm">
                        {flow.type === 'workflow' ? 'Workflow' : 'Tool'}
                      </Badge>
                      {flow.requiresHitl && (
                        <Badge variant="hitl" size="sm" dot>
                          HITL
                        </Badge>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-text-secondary leading-relaxed">{flow.description}</p>
                  <code className="text-xs text-text-muted font-mono mt-2 block">{flow.endpointId}</code>
                </Card>
              ))}
            </div>

            <div className="col-span-8 space-y-6">
              <Card variant="elevated">
                <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4 label-uppercase">
                  Input
                </h2>
                <div className="space-y-4">
                  {selectedFlow?.inputFields.map((field) => (
                    <div key={field.name}>
                      {field.type === 'select' ? (
                        <div className="space-y-2">
                          <label className="flex items-center justify-between">
                            <span className="text-sm font-medium text-text-secondary">{field.name}</span>
                            {fieldErrors[field.name] && (
                              <span className="text-xs text-danger">{fieldErrors[field.name]}</span>
                            )}
                          </label>
                          <select
                            className="w-full px-4 py-3 bg-bg-secondary/80 border border-border-subtle rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary/50 disabled:opacity-50"
                            value={formValues[field.name] ?? field.placeholder}
                            onChange={(e) => setFormValues((prev) => ({ ...prev, [field.name]: e.target.value }))}
                            disabled={isLoading}
                          >
                            {field.options?.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      ) : (
                        <InputField
                          label={field.name}
                          value={formValues[field.name] ?? ''}
                          onChange={(v) => setFormValues((prev) => ({ ...prev, [field.name]: v }))}
                          placeholder={field.placeholder}
                          disabled={isLoading}
                          error={fieldErrors[field.name]}
                        />
                      )}
                    </div>
                  ))}
                  {selectedFlow?.requiresHitl && (
                    <InputField
                      label="HITL Token"
                      value={hitlToken}
                      onChange={setHitlToken}
                      placeholder="Optional confirmation token for breach notice"
                      disabled={isLoading}
                      hint="Required for Tier C mutation tools"
                    />
                  )}
                  <div className="flex justify-end pt-2">
                    <Button
                      onClick={handleSubmit}
                      loading={isLoading}
                      disabled={serverStatus !== 'online'}
                      icon={
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      }
                    >
                      Execute
                    </Button>
                  </div>
                </div>
              </Card>

              <div className="space-y-4">
                <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider px-1 label-uppercase">
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
                                <p className="text-xs text-text-muted font-mono">{String(currentResult.correlation_id)}</p>
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
                      <p className="text-text-muted">Select a flow and execute to see results</p>
                      <p className="text-xs text-text-disabled mt-1">Results appear here with full JSON response</p>
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

      <footer className="border-t border-border-subtle mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-sm text-text-muted">
                Powered by <span className="text-text-secondary font-medium">Metacogna</span>
              </span>
              <div className="h-4 w-px bg-border-subtle" />
              <span className="text-xs text-text-muted">FastAPI + LangGraph + Pydantic</span>
            </div>
            <div className="flex items-center gap-4">
              <StatusIndicator
                status={serverStatus}
                label={serverStatus === 'online' ? 'MCP Ready' : serverStatus === 'loading' ? '…' : 'Offline'}
              />
              {healthState.data && (
                <span className="text-xs text-text-muted font-mono">v{healthState.data.version}</span>
              )}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
