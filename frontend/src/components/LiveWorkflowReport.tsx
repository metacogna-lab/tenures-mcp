import { useState, useEffect, useCallback } from 'react';
import { Badge } from './Badge';
import { Card } from './Card';
import { Button } from './Button';

type StepStatus = 'pending' | 'running' | 'completed' | 'error';

interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: StepStatus;
  data: Record<string, unknown> | null;
  duration: number | null;
}

// Mock data generators
const generatePropertyDetails = () => ({
  address: { street: '42 Harbour View Drive', suburb: 'Manly', state: 'NSW', postcode: '2095' },
  listing: { status: 'For Sale', price_guide: '$2,800,000 - $3,100,000', days_on_market: 44, agent: { name: 'Sarah Mitchell', phone: '0412 345 678' } },
  property: { type: 'House', bedrooms: 4, bathrooms: 3, parking: 2, land_size: '650 sqm' },
  open_homes: { total_held: 6, total_attendees: 47, next_scheduled: '2026-02-01 11:00' },
});

const generateFeedbackAnalysis = () => ({
  total_feedback_entries: 47,
  sentiment_breakdown: { positive: { count: 28, percentage: 59.6 }, neutral: { count: 12, percentage: 25.5 }, negative: { count: 7, percentage: 14.9 } },
  category_analysis: { location: { score: 4.5, mentions: 32 }, price: { score: 3.2, mentions: 18 }, condition: { score: 4.1, mentions: 25 }, layout: { score: 4.3, mentions: 21 } },
  top_comments: [
    { text: 'Absolutely stunning harbour views from every room', sentiment: 'positive' },
    { text: 'Kitchen renovation is high quality', sentiment: 'positive' },
    { text: 'Price seems high for current market', sentiment: 'negative' },
  ],
  buyer_intent: { high_interest: 8, moderate_interest: 15, just_looking: 24 },
});

const generateVendorReport = () => ({
  report_id: `RPT-${Date.now()}`,
  generated_at: new Date().toISOString(),
  executive_summary: 'Strong buyer interest continues with positive feedback trend. 8 high-interest buyers identified for immediate follow-up.',
  market_insights: {
    comparable_sales: [
      { address: '38 Harbour View Drive', price: '$2,950,000', date: '2025-11-20' },
      { address: '15 Ocean Road, Manly', price: '$3,100,000', date: '2025-12-05' },
    ],
    market_trend: 'Stable with slight upward pressure',
    median_dom: 38,
  },
  recommendations: [
    { priority: 'high', action: 'Follow up with 8 high-interest buyers from Saturday open home' },
    { priority: 'medium', action: 'Address parking concerns in marketing materials' },
    { priority: 'low', action: 'Schedule mid-week twilight inspection' },
  ],
});

const generateLedgerSummary = () => ({
  tenant: { name: 'John & Sarah Thompson', email: 'thompson.j@email.com', phone: '0423 456 789' },
  property: { address: '15/42 Beach Road, Bondi NSW 2026', weekly_rent: 850, bond_held: 3400 },
  financial: { current_balance: -3200, days_in_arrears: 14, last_payment: { amount: 850, date: '2026-01-14' } },
  payment_history: { on_time: 10, late_1_7: 1, late_8_14: 1, late_14_plus: 0, reliability_score: 83 },
});

const generateBreachStatus = () => ({
  is_in_arrears: true,
  days_overdue: 14,
  amount_overdue: 3200,
  breach_threshold_met: true,
  risk_level: 'high',
  risk_score: 78,
  risk_factors: [
    { factor: 'Days in arrears', impact: 'high', value: '14 days' },
    { factor: 'Amount outstanding', impact: 'high', value: '$3,200' },
    { factor: 'Payment history', impact: 'low', value: '83% reliability' },
  ],
  communication_history: [
    { date: '2026-01-21', type: 'SMS', message: 'Rent reminder sent' },
    { date: '2026-01-24', type: 'Email', message: 'Arrears notice sent' },
    { date: '2026-01-27', type: 'Phone', message: 'Attempted contact - no answer' },
  ],
});

const generateRiskClassification = () => ({
  overall_level: 'high',
  requires_immediate_action: true,
  recommended_action: 'Issue breach notice for non-payment of rent',
  compliance_checklist: [
    { item: 'Correct notice period calculated', status: 'verified' },
    { item: 'Previous communications documented', status: 'verified' },
    { item: 'Manager approval required', status: 'pending' },
  ],
  breach_notice: { form: 'Form 8 (NSW)', termination_date: '2026-02-11', amount_to_remedy: '$3,200.00' },
  workflow: [
    { step: 1, action: 'Review breach notice draft', assignee: 'Property Manager', deadline: 'Today' },
    { step: 2, action: 'Manager approval (HITL)', assignee: 'Senior PM', deadline: 'Today' },
    { step: 3, action: 'Issue breach notice', assignee: 'System', deadline: 'Upon approval' },
  ],
});

const generateDocuments = () => ({
  documents: [
    { id: 'doc_001', name: 'Smoke Alarm Certificate', type: 'compliance', expiry: '2026-08-15', status: 'valid' },
    { id: 'doc_002', name: 'Pool Safety Certificate', type: 'compliance', expiry: '2028-06-20', status: 'valid' },
    { id: 'doc_003', name: 'Electrical Safety Inspection', type: 'compliance', expiry: '2027-03-10', status: 'valid' },
    { id: 'doc_004', name: 'Gas Compliance Certificate', type: 'compliance', expiry: '2027-09-01', status: 'valid' },
  ],
});

const generateOCRResults = () => ({
  documents_processed: 4,
  successful: 4,
  total_pages: 12,
  processing_time_ms: 3420,
  extracted_fields: [
    { doc: 'Smoke Alarm Certificate', fields: { property: '15/42 Beach Road, Bondi', expiry: '2026-08-15', status: 'COMPLIANT' } },
    { doc: 'Pool Safety Certificate', fields: { property: '15/42 Beach Road, Bondi', expiry: '2028-06-20', status: 'PASS' } },
    { doc: 'Electrical Safety', fields: { property: '15/42 Beach Road, Bondi', expiry: '2027-03-10', status: 'Compliant' } },
    { doc: 'Gas Certificate', fields: { property: '15/42 Beach Road, Bondi', expiry: '2027-09-01', status: 'PASS' } },
  ],
});

const generateExpiryDates = () => ({
  total_dates: 8,
  expiry_calendar: [
    { document: 'Smoke Alarm Certificate', date: '2026-08-15', days_until: 199, urgency: 'normal' },
    { document: 'Electrical Safety', date: '2027-03-10', days_until: 406, urgency: 'low' },
    { document: 'Gas Certificate', date: '2027-09-01', days_until: 581, urgency: 'low' },
    { document: 'Pool Safety Certificate', date: '2028-06-20', days_until: 873, urgency: 'low' },
  ],
});

const generateComplianceAudit = () => ({
  overall_status: 'COMPLIANT',
  compliance_score: 100,
  issues_found: 0,
  warnings: 1,
  matrix: [
    { requirement: 'Smoke Alarm Certificate', status: 'compliant', expiry: '2026-08-15' },
    { requirement: 'Pool Safety Certificate', status: 'compliant', expiry: '2028-06-20' },
    { requirement: 'Electrical Inspection', status: 'compliant', expiry: '2027-03-10' },
    { requirement: 'Gas Compliance', status: 'compliant', expiry: '2027-09-01' },
  ],
  upcoming_renewal: { document: 'Smoke Alarm Certificate', expiry: '2026-08-15', days: 199, cost: '$150-200' },
  recommendations: [
    { priority: 'low', action: 'Schedule smoke alarm renewal for July 2026' },
    { priority: 'info', action: 'All other certificates valid for 12+ months' },
  ],
});

type WorkflowType = 'vendor_report' | 'arrears_detection' | 'compliance_audit';

const WORKFLOW_CONFIGS: Record<WorkflowType, { name: string; description: string; inputLabel: string; inputPlaceholder: string; steps: Omit<WorkflowStep, 'status' | 'data' | 'duration'>[]; dataGenerators: (() => Record<string, unknown>)[] }> = {
  vendor_report: {
    name: 'Weekly Vendor Report',
    description: 'Generate a comprehensive vendor report with property insights',
    inputLabel: 'property_id',
    inputPlaceholder: 'prop_001',
    steps: [
      { id: 'fetch_property', name: 'Property Details', description: 'Fetching property listing from VaultRE', icon: '🏠' },
      { id: 'analyze_feedback', name: 'Feedback Analysis', description: 'Analyzing open home visitor sentiment', icon: '💬' },
      { id: 'generate_report', name: 'Report Generation', description: 'Compiling insights and recommendations', icon: '📊' },
    ],
    dataGenerators: [generatePropertyDetails, generateFeedbackAnalysis, generateVendorReport],
  },
  arrears_detection: {
    name: 'Arrears Detection',
    description: 'Assess tenant arrears and generate breach workflow',
    inputLabel: 'tenancy_id',
    inputPlaceholder: 'tenancy_001',
    steps: [
      { id: 'fetch_ledger', name: 'Ledger Summary', description: 'Retrieving tenancy ledger from Ailo', icon: '💰' },
      { id: 'calculate_breach', name: 'Breach Assessment', description: 'Calculating arrears and breach status', icon: '⚠️' },
      { id: 'classify_risk', name: 'Risk Classification', description: 'Generating action workflow', icon: '📋' },
    ],
    dataGenerators: [generateLedgerSummary, generateBreachStatus, generateRiskClassification],
  },
  compliance_audit: {
    name: 'Compliance Audit',
    description: 'Audit property compliance documents and expiry dates',
    inputLabel: 'property_id',
    inputPlaceholder: 'prop_002',
    steps: [
      { id: 'fetch_documents', name: 'Document Retrieval', description: 'Fetching compliance documents', icon: '📁' },
      { id: 'ocr_documents', name: 'OCR Processing', description: 'Extracting text from documents', icon: '🔍' },
      { id: 'extract_dates', name: 'Date Extraction', description: 'Parsing expiry and due dates', icon: '📅' },
      { id: 'audit_compliance', name: 'Compliance Audit', description: 'Verifying regulatory compliance', icon: '✅' },
    ],
    dataGenerators: [generateDocuments, generateOCRResults, generateExpiryDates, generateComplianceAudit],
  },
};

export function LiveWorkflowReport() {
  const [workflowType, setWorkflowType] = useState<WorkflowType>('vendor_report');
  const [inputValue, setInputValue] = useState(WORKFLOW_CONFIGS.vendor_report.inputPlaceholder);
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [totalDuration, setTotalDuration] = useState(0);

  const config = WORKFLOW_CONFIGS[workflowType];

  // Initialize steps when workflow type changes
  useEffect(() => {
    setSteps(config.steps.map(s => ({ ...s, status: 'pending', data: null, duration: null })));
    setInputValue(config.inputPlaceholder);
    setIsComplete(false);
    setTotalDuration(0);
  }, [workflowType, config]);

  const runWorkflow = useCallback(async () => {
    setIsRunning(true);
    setIsComplete(false);
    setTotalDuration(0);
    
    // Reset steps
    setSteps(config.steps.map(s => ({ ...s, status: 'pending', data: null, duration: null })));
    
    const startTime = Date.now();
    
    for (let i = 0; i < config.steps.length; i++) {
      // Set running
      setSteps(prev => prev.map((s, idx) => idx === i ? { ...s, status: 'running' } : s));
      
      // Simulate processing time
      const processingTime = 600 + Math.random() * 1200;
      await new Promise(r => setTimeout(r, processingTime));
      
      // Generate data and complete
      const data = config.dataGenerators[i]();
      setSteps(prev => prev.map((s, idx) => 
        idx === i ? { ...s, status: 'completed', data, duration: Math.round(processingTime) } : s
      ));
    }
    
    setTotalDuration(Date.now() - startTime);
    setIsComplete(true);
    setIsRunning(false);
  }, [config]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const getStepData = (stepId: string) => {
    return steps.find(s => s.id === stepId)?.data as Record<string, unknown> | null;
  };

  const getStepStatus = (stepId: string): StepStatus => {
    return steps.find(s => s.id === stepId)?.status || 'pending';
  };

  // Render step header with status
  const StepHeader = ({ stepId, title }: { stepId: string; title: string }) => {
    const step = steps.find(s => s.id === stepId);
    if (!step) return null;

    return (
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-lg ${
            step.status === 'completed' ? 'bg-success/20' :
            step.status === 'running' ? 'bg-accent-primary/20 animate-pulse' :
            'bg-bg-secondary'
          }`}>
            {step.status === 'completed' ? (
              <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : step.status === 'running' ? (
              <svg className="w-4 h-4 text-accent-primary animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <span className="text-sm">{step.icon}</span>
            )}
          </div>
          <div>
            <h3 className="font-semibold text-text-primary">{title}</h3>
            <p className="text-xs text-text-muted">{step.description}</p>
          </div>
        </div>
        {step.duration && (
          <span className="text-xs text-text-muted font-mono bg-bg-secondary px-2 py-1 rounded">
            {step.duration}ms
          </span>
        )}
      </div>
    );
  };

  // Placeholder for pending/running steps
  const StepPlaceholder = ({ lines = 3 }: { lines?: number }) => (
    <div className="space-y-3 animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-4 bg-bg-secondary rounded" style={{ width: `${70 + Math.random() * 30}%` }} />
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Workflow Selector */}
      <div className="flex items-center gap-4 flex-wrap">
        <span className="text-sm font-medium text-text-secondary">Workflow:</span>
        <div className="flex gap-2">
          {(Object.keys(WORKFLOW_CONFIGS) as WorkflowType[]).map(type => (
            <button
              key={type}
              onClick={() => setWorkflowType(type)}
              disabled={isRunning}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                workflowType === type
                  ? 'bg-accent-primary text-white'
                  : 'bg-bg-tertiary text-text-secondary hover:bg-bg-hover'
              } disabled:opacity-50`}
            >
              {WORKFLOW_CONFIGS[type].name}
            </button>
          ))}
        </div>
      </div>

      {/* Input & Execute */}
      <Card variant="elevated" padding="md">
        <div className="flex items-end gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-text-secondary mb-2">{config.inputLabel}</label>
            <input
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              disabled={isRunning}
              className="w-full px-4 py-3 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary disabled:opacity-50"
            />
          </div>
          <Button onClick={runWorkflow} loading={isRunning} disabled={!inputValue}>
            {isRunning ? 'Processing...' : 'Run Workflow'}
          </Button>
        </div>
        
        {/* Progress bar */}
        {(isRunning || isComplete) && (
          <div className="mt-4 pt-4 border-t border-border-subtle">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-text-muted">
                {isComplete ? 'Workflow Complete' : `Processing step ${steps.filter(s => s.status === 'completed').length + 1} of ${steps.length}`}
              </span>
              {isComplete && <span className="text-sm text-success font-medium">{totalDuration}ms total</span>}
            </div>
            <div className="h-2 bg-bg-secondary rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${isComplete ? 'bg-success' : 'bg-accent-primary'}`}
                style={{ width: `${(steps.filter(s => s.status === 'completed').length / steps.length) * 100}%` }}
              />
            </div>
          </div>
        )}
      </Card>

      {/* Live Report - Vendor Report */}
      {workflowType === 'vendor_report' && (
        <div className="space-y-6">
          {/* Section 1: Property Details */}
          <Card variant={getStepStatus('fetch_property') === 'completed' ? 'elevated' : 'default'} 
                className={getStepStatus('fetch_property') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="fetch_property" title="Property Details" />
            {getStepStatus('fetch_property') === 'completed' && getStepData('fetch_property') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('fetch_property') as ReturnType<typeof generatePropertyDetails>;
                  return (
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-xl font-bold text-text-primary">{data.address.street}</h4>
                        <p className="text-text-secondary">{data.address.suburb} {data.address.state} {data.address.postcode}</p>
                        <div className="mt-4 flex items-center gap-4">
                          <Badge variant="success">{data.listing.status}</Badge>
                          <span className="text-2xl font-bold text-accent-primary">{data.listing.price_guide}</span>
                        </div>
                        <p className="text-sm text-text-muted mt-2">{data.listing.days_on_market} days on market</p>
                      </div>
                      <div className="grid grid-cols-4 gap-3">
                        {[
                          { label: 'Beds', value: data.property.bedrooms },
                          { label: 'Baths', value: data.property.bathrooms },
                          { label: 'Cars', value: data.property.parking },
                          { label: 'Land', value: data.property.land_size },
                        ].map(item => (
                          <div key={item.label} className="text-center p-3 bg-bg-secondary rounded-lg">
                            <div className="text-xl font-bold text-text-primary">{item.value}</div>
                            <div className="text-xs text-text-muted">{item.label}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('fetch_property') !== 'pending' ? (
              <StepPlaceholder lines={4} />
            ) : (
              <div className="text-center py-8 text-text-muted">Run workflow to load property details</div>
            )}
          </Card>

          {/* Section 2: Feedback Analysis */}
          <Card variant={getStepStatus('analyze_feedback') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('analyze_feedback') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="analyze_feedback" title="Feedback Analysis" />
            {getStepStatus('analyze_feedback') === 'completed' && getStepData('analyze_feedback') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('analyze_feedback') as ReturnType<typeof generateFeedbackAnalysis>;
                  return (
                    <div className="space-y-6">
                      {/* Sentiment Bar */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-text-secondary">Sentiment Distribution</span>
                          <span className="text-sm text-text-muted">{data.total_feedback_entries} responses</span>
                        </div>
                        <div className="h-6 rounded-full overflow-hidden flex">
                          <div className="bg-success h-full flex items-center justify-center text-xs text-white font-medium" style={{ width: `${data.sentiment_breakdown.positive.percentage}%` }}>
                            {data.sentiment_breakdown.positive.percentage.toFixed(0)}%
                          </div>
                          <div className="bg-warning h-full flex items-center justify-center text-xs text-black font-medium" style={{ width: `${data.sentiment_breakdown.neutral.percentage}%` }}>
                            {data.sentiment_breakdown.neutral.percentage.toFixed(0)}%
                          </div>
                          <div className="bg-danger h-full flex items-center justify-center text-xs text-white font-medium" style={{ width: `${data.sentiment_breakdown.negative.percentage}%` }}>
                            {data.sentiment_breakdown.negative.percentage.toFixed(0)}%
                          </div>
                        </div>
                        <div className="flex justify-between mt-2 text-xs text-text-muted">
                          <span>Positive ({data.sentiment_breakdown.positive.count})</span>
                          <span>Neutral ({data.sentiment_breakdown.neutral.count})</span>
                          <span>Negative ({data.sentiment_breakdown.negative.count})</span>
                        </div>
                      </div>
                      
                      {/* Category Scores & Buyer Intent */}
                      <div className="grid grid-cols-2 gap-6">
                        <div>
                          <h4 className="text-sm font-medium text-text-secondary mb-3">Category Scores</h4>
                          <div className="space-y-2">
                            {Object.entries(data.category_analysis).map(([cat, info]) => (
                              <div key={cat} className="flex items-center gap-3">
                                <span className="text-sm text-text-muted capitalize w-20">{cat}</span>
                                <div className="flex-1 h-2 bg-bg-secondary rounded-full overflow-hidden">
                                  <div className="h-full bg-accent-primary" style={{ width: `${(info.score / 5) * 100}%` }} />
                                </div>
                                <span className="text-sm font-medium text-text-primary w-8">{info.score}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-text-secondary mb-3">Buyer Intent</h4>
                          <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg border border-success/20">
                              <span className="text-success font-medium">High Interest</span>
                              <span className="text-2xl font-bold text-success">{data.buyer_intent.high_interest}</span>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg">
                              <span className="text-text-secondary">Moderate Interest</span>
                              <span className="text-xl font-bold text-text-primary">{data.buyer_intent.moderate_interest}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Top Comments */}
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-3">Recent Feedback</h4>
                        <div className="space-y-2">
                          {data.top_comments.map((comment, i) => (
                            <div key={i} className={`p-3 rounded-lg border ${
                              comment.sentiment === 'positive' ? 'bg-success/5 border-success/20' : 'bg-danger/5 border-danger/20'
                            }`}>
                              <p className="text-text-primary">"{comment.text}"</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('analyze_feedback') !== 'pending' ? (
              <StepPlaceholder lines={6} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for property details...</div>
            )}
          </Card>

          {/* Section 3: Report & Recommendations */}
          <Card variant={getStepStatus('generate_report') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('generate_report') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="generate_report" title="Report & Recommendations" />
            {getStepStatus('generate_report') === 'completed' && getStepData('generate_report') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('generate_report') as ReturnType<typeof generateVendorReport>;
                  return (
                    <div className="space-y-6">
                      {/* Executive Summary */}
                      <div className="p-4 bg-accent-primary/10 rounded-lg border border-accent-primary/20">
                        <h4 className="font-semibold text-accent-primary mb-2">Executive Summary</h4>
                        <p className="text-text-primary">{data.executive_summary}</p>
                      </div>

                      {/* Comparable Sales */}
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-3">Comparable Sales</h4>
                        <div className="overflow-hidden rounded-lg border border-border-subtle">
                          <table className="w-full">
                            <thead className="bg-bg-secondary">
                              <tr>
                                <th className="text-left py-2 px-4 text-sm text-text-muted">Address</th>
                                <th className="text-right py-2 px-4 text-sm text-text-muted">Sold Price</th>
                                <th className="text-right py-2 px-4 text-sm text-text-muted">Date</th>
                              </tr>
                            </thead>
                            <tbody>
                              {data.market_insights.comparable_sales.map((sale, i) => (
                                <tr key={i} className="border-t border-border-subtle">
                                  <td className="py-2 px-4 text-text-primary">{sale.address}</td>
                                  <td className="py-2 px-4 text-right font-semibold text-success">{sale.price}</td>
                                  <td className="py-2 px-4 text-right text-text-muted">{formatDate(sale.date)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* Recommendations */}
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-3">Recommended Actions</h4>
                        <div className="space-y-2">
                          {data.recommendations.map((rec, i) => (
                            <div key={i} className={`flex items-center gap-3 p-3 rounded-lg border ${
                              rec.priority === 'high' ? 'bg-danger/5 border-danger/20' :
                              rec.priority === 'medium' ? 'bg-warning/5 border-warning/20' :
                              'bg-info/5 border-info/20'
                            }`}>
                              <Badge variant={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'info'}>
                                {rec.priority}
                              </Badge>
                              <span className="text-text-primary">{rec.action}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('generate_report') !== 'pending' ? (
              <StepPlaceholder lines={8} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for feedback analysis...</div>
            )}
          </Card>
        </div>
      )}

      {/* Live Report - Arrears Detection */}
      {workflowType === 'arrears_detection' && (
        <div className="space-y-6">
          {/* Section 1: Ledger Summary */}
          <Card variant={getStepStatus('fetch_ledger') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('fetch_ledger') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="fetch_ledger" title="Tenancy Ledger" />
            {getStepStatus('fetch_ledger') === 'completed' && getStepData('fetch_ledger') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('fetch_ledger') as ReturnType<typeof generateLedgerSummary>;
                  return (
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-12 h-12 rounded-full bg-bg-secondary flex items-center justify-center text-2xl">👤</div>
                          <div>
                            <h4 className="font-semibold text-text-primary">{data.tenant.name}</h4>
                            <p className="text-sm text-text-muted">{data.tenant.email}</p>
                          </div>
                        </div>
                        <p className="text-text-secondary">{data.property.address}</p>
                        <p className="text-sm text-text-muted mt-1">Weekly rent: ${data.property.weekly_rent}</p>
                      </div>
                      <div className="space-y-3">
                        <div className="p-4 bg-danger/10 rounded-lg border border-danger/20">
                          <div className="text-sm text-text-muted">Current Balance</div>
                          <div className="text-3xl font-bold text-danger">${Math.abs(data.financial.current_balance).toLocaleString()}</div>
                          <div className="text-sm text-danger">{data.financial.days_in_arrears} days overdue</div>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg">
                          <span className="text-text-muted">Reliability Score</span>
                          <span className={`text-xl font-bold ${data.payment_history.reliability_score >= 80 ? 'text-success' : 'text-warning'}`}>
                            {data.payment_history.reliability_score}%
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('fetch_ledger') !== 'pending' ? (
              <StepPlaceholder lines={4} />
            ) : (
              <div className="text-center py-8 text-text-muted">Run workflow to load ledger</div>
            )}
          </Card>

          {/* Section 2: Breach Assessment */}
          <Card variant={getStepStatus('calculate_breach') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('calculate_breach') === 'completed' ? 'border-danger/20' : ''}>
            <StepHeader stepId="calculate_breach" title="Breach Assessment" />
            {getStepStatus('calculate_breach') === 'completed' && getStepData('calculate_breach') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('calculate_breach') as ReturnType<typeof generateBreachStatus>;
                  return (
                    <div className="space-y-6">
                      {/* Risk Score */}
                      <div className="flex items-center gap-8">
                        <div className="relative w-24 h-24">
                          <svg className="w-24 h-24 transform -rotate-90">
                            <circle cx="48" cy="48" r="40" fill="none" stroke="currentColor" className="text-bg-secondary" strokeWidth="8" />
                            <circle cx="48" cy="48" r="40" fill="none" stroke="currentColor" className="text-danger" strokeWidth="8"
                              strokeDasharray={`${(data.risk_score / 100) * 251} 251`} strokeLinecap="round" />
                          </svg>
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-2xl font-bold text-danger">{data.risk_score}</span>
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="error" size="md">{data.risk_level.toUpperCase()} RISK</Badge>
                            {data.breach_threshold_met && <Badge variant="warning">Breach Threshold Met</Badge>}
                          </div>
                          <div className="space-y-2">
                            {data.risk_factors.map((factor, i) => (
                              <div key={i} className="flex items-center justify-between text-sm">
                                <span className="text-text-muted">{factor.factor}</span>
                                <div className="flex items-center gap-2">
                                  <span className="text-text-primary">{factor.value}</span>
                                  <Badge variant={factor.impact === 'high' ? 'error' : 'info'} size="sm">{factor.impact}</Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Communication History */}
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-3">Communication History</h4>
                        <div className="space-y-2">
                          {data.communication_history.map((comm, i) => (
                            <div key={i} className="flex items-center gap-3 p-2 bg-bg-secondary rounded-lg">
                              <span className="text-lg">{comm.type === 'SMS' ? '💬' : comm.type === 'Email' ? '📧' : '📞'}</span>
                              <span className="text-xs text-text-muted">{formatDate(comm.date)}</span>
                              <span className="text-sm text-text-primary">{comm.message}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('calculate_breach') !== 'pending' ? (
              <StepPlaceholder lines={6} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for ledger data...</div>
            )}
          </Card>

          {/* Section 3: Risk Classification & Action */}
          <Card variant={getStepStatus('classify_risk') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('classify_risk') === 'completed' ? 'border-danger/20' : ''}>
            <StepHeader stepId="classify_risk" title="Action Workflow" />
            {getStepStatus('classify_risk') === 'completed' && getStepData('classify_risk') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('classify_risk') as ReturnType<typeof generateRiskClassification>;
                  return (
                    <div className="space-y-6">
                      {/* Breach Notice Preview */}
                      <div className="p-4 bg-danger/10 rounded-lg border border-danger/20">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-2xl">⚠️</span>
                          <h4 className="font-semibold text-danger">{data.breach_notice.form}</h4>
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <div className="text-sm text-text-muted">Termination Date</div>
                            <div className="font-medium text-text-primary">{formatDate(data.breach_notice.termination_date)}</div>
                          </div>
                          <div>
                            <div className="text-sm text-text-muted">Amount to Remedy</div>
                            <div className="font-bold text-danger text-xl">{data.breach_notice.amount_to_remedy}</div>
                          </div>
                          <div className="flex items-center">
                            <Badge variant="warning" size="md">Requires HITL Approval</Badge>
                          </div>
                        </div>
                      </div>

                      {/* Compliance Checklist */}
                      <div className="grid grid-cols-2 gap-6">
                        <div>
                          <h4 className="text-sm font-medium text-text-secondary mb-3">Compliance Checklist</h4>
                          <div className="space-y-2">
                            {data.compliance_checklist.map((item, i) => (
                              <div key={i} className="flex items-center gap-2 p-2 bg-bg-secondary rounded-lg">
                                {item.status === 'verified' ? (
                                  <div className="w-5 h-5 rounded-full bg-success/20 flex items-center justify-center">
                                    <svg className="w-3 h-3 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                    </svg>
                                  </div>
                                ) : (
                                  <div className="w-5 h-5 rounded-full bg-warning/20 flex items-center justify-center">
                                    <div className="w-2 h-2 rounded-full bg-warning" />
                                  </div>
                                )}
                                <span className={item.status === 'verified' ? 'text-text-primary' : 'text-warning'}>{item.item}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-text-secondary mb-3">Immediate Actions</h4>
                          <div className="space-y-2">
                            {data.workflow.map((item) => (
                              <div key={item.step} className="flex items-start gap-3 p-2 bg-bg-secondary rounded-lg">
                                <div className="w-6 h-6 rounded-full bg-accent-primary text-white flex items-center justify-center text-xs font-medium flex-shrink-0">
                                  {item.step}
                                </div>
                                <div className="flex-1">
                                  <div className="text-sm font-medium text-text-primary">{item.action}</div>
                                  <div className="text-xs text-text-muted">{item.assignee} • {item.deadline}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('classify_risk') !== 'pending' ? (
              <StepPlaceholder lines={8} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for breach assessment...</div>
            )}
          </Card>
        </div>
      )}

      {/* Live Report - Compliance Audit */}
      {workflowType === 'compliance_audit' && (
        <div className="space-y-6">
          {/* Section 1: Documents */}
          <Card variant={getStepStatus('fetch_documents') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('fetch_documents') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="fetch_documents" title="Compliance Documents" />
            {getStepStatus('fetch_documents') === 'completed' && getStepData('fetch_documents') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('fetch_documents') as ReturnType<typeof generateDocuments>;
                  return (
                    <div className="grid grid-cols-2 gap-3">
                      {data.documents.map((doc) => (
                        <div key={doc.id} className="flex items-center gap-3 p-3 bg-bg-secondary rounded-lg">
                          <span className="text-2xl">📋</span>
                          <div className="flex-1">
                            <div className="font-medium text-text-primary">{doc.name}</div>
                            <div className="text-xs text-text-muted">Expires: {formatDate(doc.expiry)}</div>
                          </div>
                          <Badge variant="success" size="sm">{doc.status}</Badge>
                        </div>
                      ))}
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('fetch_documents') !== 'pending' ? (
              <StepPlaceholder lines={4} />
            ) : (
              <div className="text-center py-8 text-text-muted">Run workflow to fetch documents</div>
            )}
          </Card>

          {/* Section 2: OCR Processing */}
          <Card variant={getStepStatus('ocr_documents') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('ocr_documents') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="ocr_documents" title="OCR Processing" />
            {getStepStatus('ocr_documents') === 'completed' && getStepData('ocr_documents') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('ocr_documents') as ReturnType<typeof generateOCRResults>;
                  return (
                    <div className="space-y-4">
                      <div className="grid grid-cols-4 gap-3">
                        {[
                          { label: 'Processed', value: data.documents_processed },
                          { label: 'Successful', value: data.successful, color: 'text-success' },
                          { label: 'Total Pages', value: data.total_pages },
                          { label: 'Time', value: `${(data.processing_time_ms / 1000).toFixed(1)}s` },
                        ].map((stat) => (
                          <div key={stat.label} className="text-center p-3 bg-bg-secondary rounded-lg">
                            <div className={`text-2xl font-bold ${stat.color || 'text-text-primary'}`}>{stat.value}</div>
                            <div className="text-xs text-text-muted">{stat.label}</div>
                          </div>
                        ))}
                      </div>
                      <div className="space-y-2">
                        {data.extracted_fields.map((item, i) => (
                          <div key={i} className="p-3 bg-bg-secondary rounded-lg">
                            <div className="font-medium text-text-primary mb-2">{item.doc}</div>
                            <div className="grid grid-cols-3 gap-2 text-sm">
                              {Object.entries(item.fields).map(([key, value]) => (
                                <div key={key}>
                                  <span className="text-text-muted capitalize">{key}: </span>
                                  <span className="text-text-primary">{value}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('ocr_documents') !== 'pending' ? (
              <StepPlaceholder lines={6} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for documents...</div>
            )}
          </Card>

          {/* Section 3: Expiry Timeline */}
          <Card variant={getStepStatus('extract_dates') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('extract_dates') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="extract_dates" title="Expiry Timeline" />
            {getStepStatus('extract_dates') === 'completed' && getStepData('extract_dates') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('extract_dates') as ReturnType<typeof generateExpiryDates>;
                  return (
                    <div className="relative pl-8">
                      <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-border-subtle" />
                      <div className="space-y-4">
                        {data.expiry_calendar.map((item, i) => (
                          <div key={i} className="relative">
                            <div className={`absolute left-[-22px] w-4 h-4 rounded-full border-2 ${
                              item.urgency === 'normal' ? 'bg-warning border-warning' : 'bg-success border-success'
                            }`} />
                            <div className={`p-3 rounded-lg border ${
                              item.urgency === 'normal' ? 'bg-warning/5 border-warning/20' : 'bg-success/5 border-success/20'
                            }`}>
                              <div className="flex items-center justify-between">
                                <div>
                                  <div className="font-medium text-text-primary">{item.document}</div>
                                  <div className="text-sm text-text-muted">Expires: {formatDate(item.date)}</div>
                                </div>
                                <Badge variant={item.urgency === 'normal' ? 'warning' : 'success'}>{item.days_until} days</Badge>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('extract_dates') !== 'pending' ? (
              <StepPlaceholder lines={4} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for OCR results...</div>
            )}
          </Card>

          {/* Section 4: Compliance Audit Result */}
          <Card variant={getStepStatus('audit_compliance') === 'completed' ? 'elevated' : 'default'}
                className={getStepStatus('audit_compliance') === 'completed' ? 'border-success/20' : ''}>
            <StepHeader stepId="audit_compliance" title="Audit Result" />
            {getStepStatus('audit_compliance') === 'completed' && getStepData('audit_compliance') ? (
              <div className="animate-fade-in">
                {(() => {
                  const data = getStepData('audit_compliance') as ReturnType<typeof generateComplianceAudit>;
                  return (
                    <div className="space-y-6">
                      {/* Overall Status */}
                      <div className="flex items-center justify-between p-4 bg-success/10 rounded-lg border border-success/20">
                        <div className="flex items-center gap-4">
                          <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center">
                            <svg className="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          </div>
                          <div>
                            <div className="text-2xl font-bold text-success">{data.overall_status}</div>
                            <div className="text-text-muted">All documents verified</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-4xl font-bold text-success">{data.compliance_score}%</div>
                          <div className="text-sm text-text-muted">Compliance Score</div>
                        </div>
                      </div>

                      {/* Compliance Matrix */}
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-3">Compliance Matrix</h4>
                        <div className="overflow-hidden rounded-lg border border-border-subtle">
                          <table className="w-full">
                            <thead className="bg-bg-secondary">
                              <tr>
                                <th className="text-left py-2 px-4 text-sm text-text-muted">Requirement</th>
                                <th className="text-center py-2 px-4 text-sm text-text-muted">Status</th>
                                <th className="text-right py-2 px-4 text-sm text-text-muted">Expiry</th>
                              </tr>
                            </thead>
                            <tbody>
                              {data.matrix.map((item, i) => (
                                <tr key={i} className="border-t border-border-subtle">
                                  <td className="py-2 px-4 text-text-primary">{item.requirement}</td>
                                  <td className="py-2 px-4 text-center">
                                    <Badge variant="success" size="sm">{item.status}</Badge>
                                  </td>
                                  <td className="py-2 px-4 text-right text-text-muted">{formatDate(item.expiry)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* Recommendations */}
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-3">Recommendations</h4>
                        <div className="space-y-2">
                          {data.recommendations.map((rec, i) => (
                            <div key={i} className={`flex items-center gap-3 p-3 rounded-lg border ${
                              rec.priority === 'low' ? 'bg-info/5 border-info/20' : 'bg-bg-secondary border-border-subtle'
                            }`}>
                              <Badge variant={rec.priority === 'low' ? 'info' : 'neutral'}>{rec.priority}</Badge>
                              <span className="text-text-primary">{rec.action}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : getStepStatus('audit_compliance') !== 'pending' ? (
              <StepPlaceholder lines={8} />
            ) : (
              <div className="text-center py-8 text-text-muted">Waiting for date extraction...</div>
            )}
          </Card>
        </div>
      )}

      {/* Completion Summary */}
      {isComplete && (
        <Card variant="elevated" className="border-success/30 animate-fade-in">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-success/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-success">Workflow Complete</h3>
              <p className="text-sm text-text-muted">
                {config.name} completed {steps.length} steps in {totalDuration}ms
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
