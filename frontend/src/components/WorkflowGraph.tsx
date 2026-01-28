import { useState, useEffect, useCallback } from 'react';
import { Card } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { JsonDisplay } from './JsonDisplay';

interface WorkflowNode {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  output?: Record<string, unknown>;
  duration?: number;
}

interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  inputField: string;
  inputPlaceholder: string;
  nodes: Omit<WorkflowNode, 'status' | 'output' | 'duration'>[];
  mockExecutor: (input: string, onNodeUpdate: (nodeId: string, update: Partial<WorkflowNode>) => void) => Promise<Record<string, unknown>>;
}

// Mock data generators for realistic real estate scenarios
const generatePropertyDetails = (propertyId: string) => ({
  property_id: propertyId,
  address: {
    street: '42 Harbour View Drive',
    suburb: 'Manly',
    state: 'NSW',
    postcode: '2095',
  },
  listing: {
    status: 'For Sale',
    price_guide: '$2,800,000 - $3,100,000',
    listed_date: '2025-12-15',
    days_on_market: 44,
    agent: {
      name: 'Sarah Mitchell',
      phone: '0412 345 678',
      email: 'sarah.mitchell@raywhite.com',
    },
  },
  property: {
    type: 'House',
    bedrooms: 4,
    bathrooms: 3,
    parking: 2,
    land_size: '650 sqm',
    features: ['Harbour Views', 'Pool', 'Renovated Kitchen', 'Home Office'],
  },
  open_homes: {
    total_held: 6,
    total_attendees: 47,
    next_scheduled: '2026-02-01 11:00',
  },
});

const generateFeedbackAnalysis = (propertyId: string) => ({
  property_id: propertyId,
  analysis_timestamp: new Date().toISOString(),
  total_feedback_entries: 47,
  sentiment_breakdown: {
    positive: { count: 28, percentage: 59.6 },
    neutral: { count: 12, percentage: 25.5 },
    negative: { count: 7, percentage: 14.9 },
  },
  category_analysis: {
    location: { sentiment: 'positive', score: 4.5, mentions: 32 },
    price: { sentiment: 'neutral', score: 3.2, mentions: 18 },
    condition: { sentiment: 'positive', score: 4.1, mentions: 25 },
    layout: { sentiment: 'positive', score: 4.3, mentions: 21 },
    parking: { sentiment: 'neutral', score: 3.5, mentions: 8 },
  },
  top_positive_comments: [
    { comment: 'Absolutely stunning harbour views from every room', category: 'location', date: '2026-01-25' },
    { comment: 'Kitchen renovation is high quality, love the stone benchtops', category: 'condition', date: '2026-01-18' },
    { comment: 'Great flow between indoor and outdoor living', category: 'layout', date: '2026-01-18' },
  ],
  top_concerns: [
    { concern: 'Price seems high for current market', frequency: 5 },
    { concern: 'Street parking can be difficult on weekends', frequency: 3 },
  ],
  buyer_intent_signals: {
    high_interest: 8,
    moderate_interest: 15,
    just_looking: 24,
  },
});

const generateVendorReport = (propertyId: string, feedbackData: Record<string, unknown>) => ({
  report_id: `RPT-${Date.now()}`,
  property_id: propertyId,
  generated_at: new Date().toISOString(),
  report_type: 'Weekly Vendor Update',
  executive_summary: {
    headline: 'Strong buyer interest continues with positive feedback trend',
    key_metrics: {
      open_home_attendance: '+12% vs last week',
      buyer_enquiries: 8,
      private_inspections: 3,
      days_on_market: 44,
    },
    market_position: 'Well-positioned within price guide based on comparable sales',
  },
  feedback_summary: feedbackData,
  market_insights: {
    comparable_sales: [
      { address: '38 Harbour View Drive', sold_price: '$2,950,000', sold_date: '2025-11-20' },
      { address: '15 Ocean Road, Manly', sold_price: '$3,100,000', sold_date: '2025-12-05' },
    ],
    market_trend: 'Stable with slight upward pressure',
    median_days_on_market: 38,
  },
  recommendations: [
    { priority: 'high', action: 'Follow up with 8 high-interest buyers from Saturday open home' },
    { priority: 'medium', action: 'Consider addressing parking concern in marketing materials' },
    { priority: 'low', action: 'Schedule mid-week twilight inspection for working professionals' },
  ],
  next_steps: {
    scheduled_activities: ['Open Home: Saturday 11am-12pm', 'Private Inspection: Tuesday 2pm'],
    vendor_meeting: 'Recommended within 48 hours to discuss offer strategy',
  },
});

const generateLedgerSummary = (tenancyId: string) => ({
  tenancy_id: tenancyId,
  tenant: {
    name: 'John & Sarah Thompson',
    email: 'thompson.j@email.com',
    phone: '0423 456 789',
    lease_start: '2024-06-01',
    lease_end: '2026-05-31',
  },
  property: {
    address: '15/42 Beach Road, Bondi NSW 2026',
    weekly_rent: 850,
    bond_held: 3400,
  },
  financial_summary: {
    current_balance: -3200,
    rent_paid_to_date: '2026-01-14',
    days_in_arrears: 14,
    last_payment: {
      amount: 850,
      date: '2026-01-14',
      method: 'Direct Debit',
    },
  },
  payment_history: {
    last_12_months: {
      on_time: 10,
      late_1_7_days: 1,
      late_8_14_days: 1,
      late_14_plus_days: 0,
    },
    payment_reliability_score: 83,
  },
  arrears_history: [
    { date: '2026-01-21', amount: -1700, note: 'Rent due 14/01 unpaid' },
    { date: '2026-01-28', amount: -3200, note: 'Rent due 21/01 unpaid - 2 weeks arrears' },
  ],
});

const generateBreachStatus = (tenancyId: string, ledgerData: Record<string, unknown>) => {
  const financialSummary = (ledgerData as { financial_summary?: { days_in_arrears?: number; current_balance?: number } }).financial_summary || {};
  const daysInArrears = financialSummary.days_in_arrears || 14;
  const balance = financialSummary.current_balance || -3200;
  
  return {
    tenancy_id: tenancyId,
    assessment_date: new Date().toISOString(),
    arrears_status: {
      is_in_arrears: true,
      days_overdue: daysInArrears,
      amount_overdue: Math.abs(balance),
      breach_threshold_days: 14,
      breach_threshold_met: daysInArrears >= 14,
    },
    breach_risk: {
      level: daysInArrears >= 14 ? 'high' : daysInArrears >= 7 ? 'medium' : 'low',
      score: Math.min(100, daysInArrears * 5 + 30),
      factors: [
        { factor: 'Days in arrears', impact: 'high', value: `${daysInArrears} days` },
        { factor: 'Amount outstanding', impact: 'high', value: `$${Math.abs(balance).toLocaleString()}` },
        { factor: 'Payment history', impact: 'low', value: '83% reliability' },
      ],
    },
    regulatory_context: {
      state: 'NSW',
      notice_type: 'Non-payment of rent',
      minimum_notice_period: '14 days',
      can_issue_notice: daysInArrears >= 14,
    },
    recommended_action: daysInArrears >= 14 
      ? 'Issue breach notice for non-payment of rent'
      : 'Send reminder notice and attempt phone contact',
    communication_history: [
      { date: '2026-01-21', type: 'SMS', message: 'Rent reminder sent' },
      { date: '2026-01-24', type: 'Email', message: 'Arrears notice sent' },
      { date: '2026-01-27', type: 'Phone', message: 'Attempted contact - no answer' },
    ],
  };
};

const generateRiskClassification = (breachData: Record<string, unknown>) => {
  const breachRisk = (breachData as { breach_risk?: { level?: string; score?: number } }).breach_risk || {};
  const riskLevel = breachRisk.level || 'high';
  
  return {
    classification_timestamp: new Date().toISOString(),
    risk_assessment: {
      overall_level: riskLevel,
      confidence_score: 0.87,
      requires_immediate_action: riskLevel === 'high' || riskLevel === 'critical',
    },
    recommended_workflow: {
      immediate: [
        { step: 1, action: 'Review breach notice draft', assignee: 'Property Manager', deadline: 'Today' },
        { step: 2, action: 'Manager approval (HITL)', assignee: 'Senior PM', deadline: 'Today' },
        { step: 3, action: 'Issue breach notice', assignee: 'System', deadline: 'Upon approval' },
      ],
      follow_up: [
        { action: 'Phone call to tenant', timeline: '24 hours after notice' },
        { action: 'Payment plan discussion if contacted', timeline: 'Within 48 hours' },
        { action: 'Escalate to tribunal if no response', timeline: '14 days after notice' },
      ],
    },
    compliance_checklist: [
      { item: 'Correct notice period calculated', status: 'verified' },
      { item: 'Previous communications documented', status: 'verified' },
      { item: 'Tenant contact details current', status: 'verified' },
      { item: 'Manager approval required', status: 'pending' },
    ],
    breach_notice_preview: {
      notice_type: 'Termination Notice - Non-payment of Rent',
      form_number: 'Form 8 (NSW)',
      termination_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      amount_to_remedy: '$3,200.00',
    },
  };
};

const generateDocumentList = (propertyId: string) => ({
  property_id: propertyId,
  document_count: 8,
  documents: [
    { id: 'doc_001', name: 'Smoke Alarm Compliance Certificate', type: 'compliance', url: 'vault://docs/smoke_alarm.pdf', last_updated: '2025-08-15' },
    { id: 'doc_002', name: 'Pool Safety Certificate', type: 'compliance', url: 'vault://docs/pool_safety.pdf', last_updated: '2025-06-20' },
    { id: 'doc_003', name: 'Electrical Safety Inspection', type: 'compliance', url: 'vault://docs/electrical.pdf', last_updated: '2025-03-10' },
    { id: 'doc_004', name: 'Gas Compliance Certificate', type: 'compliance', url: 'vault://docs/gas_cert.pdf', last_updated: '2025-09-01' },
    { id: 'doc_005', name: 'Residential Tenancy Agreement', type: 'contract', url: 'vault://docs/lease.pdf', last_updated: '2024-06-01' },
    { id: 'doc_006', name: 'Condition Report - Ingoing', type: 'report', url: 'vault://docs/condition_in.pdf', last_updated: '2024-06-01' },
    { id: 'doc_007', name: 'Strata By-Laws', type: 'legal', url: 'vault://docs/bylaws.pdf', last_updated: '2023-11-15' },
    { id: 'doc_008', name: 'Building Insurance Certificate', type: 'insurance', url: 'vault://docs/insurance.pdf', last_updated: '2025-07-01' },
  ],
  compliance_summary: {
    total_compliance_docs: 4,
    up_to_date: 3,
    expiring_soon: 1,
    expired: 0,
  },
});

const generateOCRResults = () => ({
  processing_summary: {
    documents_processed: 4,
    successful: 4,
    failed: 0,
    total_pages: 12,
    processing_time_ms: 3420,
  },
  extracted_content: [
    {
      document_id: 'doc_001',
      document_name: 'Smoke Alarm Compliance Certificate',
      confidence_score: 0.96,
      extracted_text: 'SMOKE ALARM COMPLIANCE CERTIFICATE\n\nProperty: 15/42 Beach Road, Bondi NSW 2026\nInspection Date: 15 August 2025\nCertificate Valid Until: 15 August 2026\n\nCompliance Status: COMPLIANT\nAlarms Tested: 3\nBattery Status: All OK\n\nInspector: SafeHome Inspections\nLicense: NSW-SA-12345',
      key_fields: {
        property_address: '15/42 Beach Road, Bondi NSW 2026',
        inspection_date: '2025-08-15',
        expiry_date: '2026-08-15',
        status: 'COMPLIANT',
      },
    },
    {
      document_id: 'doc_002',
      document_name: 'Pool Safety Certificate',
      confidence_score: 0.94,
      extracted_text: 'SWIMMING POOL COMPLIANCE CERTIFICATE\n\nProperty: 15/42 Beach Road, Bondi NSW 2026\nIssue Date: 20 June 2025\nExpiry Date: 20 June 2028\n\nPool Registration: SP-2025-78432\nBarrier Inspection: PASS\nCPR Sign: Present\n\nCertified By: AquaSafe Inspections',
      key_fields: {
        property_address: '15/42 Beach Road, Bondi NSW 2026',
        issue_date: '2025-06-20',
        expiry_date: '2028-06-20',
        status: 'PASS',
      },
    },
    {
      document_id: 'doc_003',
      document_name: 'Electrical Safety Inspection',
      confidence_score: 0.92,
      extracted_text: 'ELECTRICAL SAFETY INSPECTION REPORT\n\nProperty: 15/42 Beach Road, Bondi NSW 2026\nInspection Date: 10 March 2025\nNext Inspection Due: 10 March 2027\n\nSwitchboard: Compliant\nSafety Switches (RCDs): 2 installed, functional\nSmoke Detector Wiring: OK\n\nElectrician: Lic. 234567C',
      key_fields: {
        property_address: '15/42 Beach Road, Bondi NSW 2026',
        inspection_date: '2025-03-10',
        next_due_date: '2027-03-10',
        status: 'Compliant',
      },
    },
    {
      document_id: 'doc_004',
      document_name: 'Gas Compliance Certificate',
      confidence_score: 0.95,
      extracted_text: 'GAS INSTALLATION COMPLIANCE CERTIFICATE\n\nProperty: 15/42 Beach Road, Bondi NSW 2026\nInspection Date: 01 September 2025\nCertificate Expiry: 01 September 2027\n\nAppliances Tested: Gas Cooktop, Gas Hot Water\nPressure Test: PASS\nVentilation: Adequate\n\nGasfitter License: GF-45678',
      key_fields: {
        property_address: '15/42 Beach Road, Bondi NSW 2026',
        inspection_date: '2025-09-01',
        expiry_date: '2027-09-01',
        status: 'PASS',
      },
    },
  ],
});

const generateExpiryDates = () => ({
  extraction_timestamp: new Date().toISOString(),
  total_dates_found: 8,
  dates_by_document: [
    {
      document_id: 'doc_001',
      document_name: 'Smoke Alarm Compliance Certificate',
      dates: [
        { date_type: 'inspection', date_value: '2025-08-15', context: 'Last inspection date' },
        { date_type: 'expiry', date_value: '2026-08-15', context: 'Certificate valid until', days_until: 199, status: 'valid' },
      ],
    },
    {
      document_id: 'doc_002',
      document_name: 'Pool Safety Certificate',
      dates: [
        { date_type: 'issue', date_value: '2025-06-20', context: 'Certificate issue date' },
        { date_type: 'expiry', date_value: '2028-06-20', context: 'Certificate expiry', days_until: 873, status: 'valid' },
      ],
    },
    {
      document_id: 'doc_003',
      document_name: 'Electrical Safety Inspection',
      dates: [
        { date_type: 'inspection', date_value: '2025-03-10', context: 'Last inspection' },
        { date_type: 'due', date_value: '2027-03-10', context: 'Next inspection due', days_until: 406, status: 'valid' },
      ],
    },
    {
      document_id: 'doc_004',
      document_name: 'Gas Compliance Certificate',
      dates: [
        { date_type: 'inspection', date_value: '2025-09-01', context: 'Inspection date' },
        { date_type: 'expiry', date_value: '2027-09-01', context: 'Certificate expiry', days_until: 581, status: 'valid' },
      ],
    },
  ],
  expiry_calendar: [
    { date: '2026-08-15', document: 'Smoke Alarm Certificate', days_until: 199, urgency: 'normal' },
    { date: '2027-03-10', document: 'Electrical Inspection', days_until: 406, urgency: 'low' },
    { date: '2027-09-01', document: 'Gas Certificate', days_until: 581, urgency: 'low' },
    { date: '2028-06-20', document: 'Pool Safety Certificate', days_until: 873, urgency: 'low' },
  ],
});

const generateComplianceAudit = () => ({
  audit_timestamp: new Date().toISOString(),
  audit_result: {
    overall_status: 'COMPLIANT',
    confidence_score: 0.94,
    documents_reviewed: 4,
    issues_found: 0,
    warnings: 1,
  },
  compliance_matrix: [
    { requirement: 'Smoke Alarm Certificate', status: 'compliant', expiry: '2026-08-15', action_required: null },
    { requirement: 'Pool Safety Certificate', status: 'compliant', expiry: '2028-06-20', action_required: null },
    { requirement: 'Electrical Inspection', status: 'compliant', expiry: '2027-03-10', action_required: null },
    { requirement: 'Gas Compliance', status: 'compliant', expiry: '2027-09-01', action_required: null },
  ],
  upcoming_renewals: [
    {
      document: 'Smoke Alarm Compliance Certificate',
      expiry_date: '2026-08-15',
      days_until_expiry: 199,
      recommended_renewal_date: '2026-07-15',
      estimated_cost: '$150-200',
      approved_providers: ['SafeHome Inspections', 'Smoke Alarm Solutions NSW'],
    },
  ],
  audit_summary: {
    last_audit: '2025-10-15',
    next_scheduled_audit: '2026-04-15',
    audit_frequency: '6 months',
    compliance_score: 100,
    trend: 'stable',
  },
  recommendations: [
    { priority: 'low', action: 'Schedule smoke alarm certificate renewal for July 2026', deadline: '2026-06-15' },
    { priority: 'info', action: 'All other certificates valid for 12+ months', deadline: null },
  ],
});

// Workflow definitions
const WORKFLOW_DEFINITIONS: WorkflowDefinition[] = [
  {
    id: 'weekly_vendor_report',
    name: 'Weekly Vendor Report',
    description: 'Generate comprehensive vendor reports with property details, feedback analysis, and market insights',
    inputField: 'property_id',
    inputPlaceholder: 'prop_001',
    nodes: [
      { id: 'fetch_property', name: 'Fetch Property', description: 'Retrieve property listing details from VaultRE', icon: '🏠' },
      { id: 'analyze_feedback', name: 'Analyze Feedback', description: 'Sentiment analysis of open home feedback', icon: '💬' },
      { id: 'generate_report', name: 'Generate Report', description: 'Compile vendor report with insights', icon: '📊' },
    ],
    mockExecutor: async (propertyId, onNodeUpdate) => {
      // Step 1: Fetch Property
      onNodeUpdate('fetch_property', { status: 'running' });
      await new Promise(r => setTimeout(r, 800));
      const propertyData = generatePropertyDetails(propertyId);
      onNodeUpdate('fetch_property', { status: 'completed', output: propertyData, duration: 800 });

      // Step 2: Analyze Feedback
      onNodeUpdate('analyze_feedback', { status: 'running' });
      await new Promise(r => setTimeout(r, 1200));
      const feedbackData = generateFeedbackAnalysis(propertyId);
      onNodeUpdate('analyze_feedback', { status: 'completed', output: feedbackData, duration: 1200 });

      // Step 3: Generate Report
      onNodeUpdate('generate_report', { status: 'running' });
      await new Promise(r => setTimeout(r, 1500));
      const reportData = generateVendorReport(propertyId, feedbackData);
      onNodeUpdate('generate_report', { status: 'completed', output: reportData, duration: 1500 });

      return reportData;
    },
  },
  {
    id: 'arrears_detection',
    name: 'Arrears Detection',
    description: 'Detect tenant arrears, assess breach risk, and generate recommended actions',
    inputField: 'tenancy_id',
    inputPlaceholder: 'tenancy_001',
    nodes: [
      { id: 'fetch_ledger', name: 'Fetch Ledger', description: 'Retrieve tenancy ledger from Ailo', icon: '💰' },
      { id: 'calculate_breach', name: 'Calculate Breach', description: 'Assess arrears and breach threshold', icon: '⚠️' },
      { id: 'classify_risk', name: 'Classify Risk', description: 'Risk classification and action plan', icon: '📋' },
    ],
    mockExecutor: async (tenancyId, onNodeUpdate) => {
      // Step 1: Fetch Ledger
      onNodeUpdate('fetch_ledger', { status: 'running' });
      await new Promise(r => setTimeout(r, 600));
      const ledgerData = generateLedgerSummary(tenancyId);
      onNodeUpdate('fetch_ledger', { status: 'completed', output: ledgerData, duration: 600 });

      // Step 2: Calculate Breach
      onNodeUpdate('calculate_breach', { status: 'running' });
      await new Promise(r => setTimeout(r, 900));
      const breachData = generateBreachStatus(tenancyId, ledgerData);
      onNodeUpdate('calculate_breach', { status: 'completed', output: breachData, duration: 900 });

      // Step 3: Classify Risk
      onNodeUpdate('classify_risk', { status: 'running' });
      await new Promise(r => setTimeout(r, 700));
      const riskData = generateRiskClassification(breachData);
      onNodeUpdate('classify_risk', { status: 'completed', output: riskData, duration: 700 });

      return riskData;
    },
  },
  {
    id: 'compliance_audit',
    name: 'Compliance Audit',
    description: 'Audit property compliance documents, extract dates, and verify regulatory compliance',
    inputField: 'property_id',
    inputPlaceholder: 'prop_002',
    nodes: [
      { id: 'fetch_documents', name: 'Fetch Documents', description: 'Retrieve compliance documents', icon: '📁' },
      { id: 'ocr_documents', name: 'OCR Processing', description: 'Extract text from documents', icon: '🔍' },
      { id: 'extract_dates', name: 'Extract Dates', description: 'Parse expiry and due dates', icon: '📅' },
      { id: 'audit_compliance', name: 'Audit Compliance', description: 'Verify compliance status', icon: '✅' },
    ],
    mockExecutor: async (propertyId, onNodeUpdate) => {
      // Step 1: Fetch Documents
      onNodeUpdate('fetch_documents', { status: 'running' });
      await new Promise(r => setTimeout(r, 500));
      const docsData = generateDocumentList(propertyId);
      onNodeUpdate('fetch_documents', { status: 'completed', output: docsData, duration: 500 });

      // Step 2: OCR Processing
      onNodeUpdate('ocr_documents', { status: 'running' });
      await new Promise(r => setTimeout(r, 2000));
      const ocrData = generateOCRResults();
      onNodeUpdate('ocr_documents', { status: 'completed', output: ocrData, duration: 2000 });

      // Step 3: Extract Dates
      onNodeUpdate('extract_dates', { status: 'running' });
      await new Promise(r => setTimeout(r, 800));
      const datesData = generateExpiryDates();
      onNodeUpdate('extract_dates', { status: 'completed', output: datesData, duration: 800 });

      // Step 4: Audit Compliance
      onNodeUpdate('audit_compliance', { status: 'running' });
      await new Promise(r => setTimeout(r, 600));
      const auditData = generateComplianceAudit();
      onNodeUpdate('audit_compliance', { status: 'completed', output: auditData, duration: 600 });

      return auditData;
    },
  },
];

interface WorkflowGraphProps {
  onWorkflowComplete?: (result: Record<string, unknown>) => void;
}

export function WorkflowGraph({ onWorkflowComplete }: WorkflowGraphProps) {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDefinition>(WORKFLOW_DEFINITIONS[0]);
  const [inputValue, setInputValue] = useState(WORKFLOW_DEFINITIONS[0].inputPlaceholder);
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [finalResult, setFinalResult] = useState<Record<string, unknown> | null>(null);
  const [totalDuration, setTotalDuration] = useState<number>(0);

  // Initialize nodes when workflow changes
  useEffect(() => {
    setNodes(selectedWorkflow.nodes.map(n => ({ ...n, status: 'pending' as const })));
    setSelectedNode(null);
    setFinalResult(null);
    setTotalDuration(0);
    setInputValue(selectedWorkflow.inputPlaceholder);
  }, [selectedWorkflow]);

  const handleNodeUpdate = useCallback((nodeId: string, update: Partial<WorkflowNode>) => {
    setNodes(prev => prev.map(n => n.id === nodeId ? { ...n, ...update } : n));
    if (update.status === 'completed' && update.output) {
      setNodes(prev => {
        const node = prev.find(n => n.id === nodeId);
        if (node) setSelectedNode({ ...node, ...update });
        return prev;
      });
    }
  }, []);

  const runWorkflow = async () => {
    setIsRunning(true);
    setFinalResult(null);
    setSelectedNode(null);
    setTotalDuration(0);
    
    // Reset all nodes
    setNodes(selectedWorkflow.nodes.map(n => ({ ...n, status: 'pending' as const, output: undefined, duration: undefined })));

    const startTime = Date.now();
    
    try {
      const result = await selectedWorkflow.mockExecutor(inputValue, handleNodeUpdate);
      setFinalResult(result);
      setTotalDuration(Date.now() - startTime);
      onWorkflowComplete?.(result);
    } catch (error) {
      console.error('Workflow error:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusColor = (status: WorkflowNode['status']) => {
    switch (status) {
      case 'completed': return 'border-success bg-success/10';
      case 'running': return 'border-accent-primary bg-accent-primary/10 animate-pulse';
      case 'error': return 'border-danger bg-danger/10';
      default: return 'border-border-subtle bg-bg-tertiary';
    }
  };

  const getStatusIcon = (status: WorkflowNode['status']) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'running':
        return (
          <svg className="w-4 h-4 text-accent-primary animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      default:
        return <span className="w-4 h-4 rounded-full border-2 border-border-default" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Workflow Selector */}
      <div className="flex items-center gap-4 flex-wrap">
        <span className="text-sm font-medium text-text-secondary">Select Workflow:</span>
        <div className="flex gap-2">
          {WORKFLOW_DEFINITIONS.map(wf => (
            <button
              key={wf.id}
              onClick={() => setSelectedWorkflow(wf)}
              disabled={isRunning}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${selectedWorkflow.id === wf.id 
                  ? 'bg-accent-primary text-white' 
                  : 'bg-bg-tertiary text-text-secondary hover:bg-bg-hover hover:text-text-primary'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {wf.name}
            </button>
          ))}
        </div>
      </div>

      {/* Workflow Description */}
      <Card variant="default" padding="md">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-text-primary flex items-center gap-2">
              {selectedWorkflow.name}
              <Badge variant="beta">LangGraph</Badge>
            </h3>
            <p className="text-sm text-text-secondary mt-1">{selectedWorkflow.description}</p>
          </div>
          <Badge variant="info" size="md">{nodes.length} Steps</Badge>
        </div>
      </Card>

      {/* Input & Execute */}
      <Card variant="elevated" padding="md">
        <div className="flex items-end gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-text-secondary mb-2">
              {selectedWorkflow.inputField}
            </label>
            <input
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              placeholder={selectedWorkflow.inputPlaceholder}
              disabled={isRunning}
              className="w-full px-4 py-3 bg-bg-secondary border border-border-subtle rounded-lg text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/50 disabled:opacity-50"
            />
          </div>
          <Button 
            onClick={runWorkflow} 
            loading={isRunning}
            disabled={!inputValue}
            icon={
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          >
            {isRunning ? 'Running...' : 'Execute Workflow'}
          </Button>
        </div>
      </Card>

      {/* Workflow Graph Visualization */}
      <div className="grid grid-cols-12 gap-6">
        {/* Graph */}
        <div className="col-span-5">
          <Card variant="default" padding="md">
            <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
              Workflow Graph
            </h4>
            <div className="relative">
              {nodes.map((node, index) => (
                <div key={node.id} className="relative">
                  {/* Connector line */}
                  {index > 0 && (
                    <div className="absolute left-6 -top-3 w-0.5 h-6 bg-border-subtle" />
                  )}
                  
                  {/* Node */}
                  <div
                    onClick={() => node.output && setSelectedNode(node)}
                    className={`
                      relative flex items-center gap-4 p-4 rounded-xl border-2 transition-all cursor-pointer
                      ${getStatusColor(node.status)}
                      ${selectedNode?.id === node.id ? 'ring-2 ring-accent-primary ring-offset-2 ring-offset-bg-primary' : ''}
                      ${node.output ? 'hover:border-accent-primary/50' : ''}
                    `}
                  >
                    {/* Status indicator */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-bg-secondary flex items-center justify-center">
                      {getStatusIcon(node.status)}
                    </div>
                    
                    {/* Node info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{node.icon}</span>
                        <h5 className="font-medium text-text-primary">{node.name}</h5>
                      </div>
                      <p className="text-xs text-text-muted truncate">{node.description}</p>
                    </div>

                    {/* Duration */}
                    {node.duration && (
                      <span className="text-xs text-text-muted font-mono">
                        {node.duration}ms
                      </span>
                    )}
                  </div>

                  {/* Arrow to next node */}
                  {index < nodes.length - 1 && (
                    <div className="flex justify-center py-2">
                      <svg className="w-4 h-4 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    </div>
                  )}
                </div>
              ))}

              {/* End node */}
              {finalResult && (
                <>
                  <div className="flex justify-center py-2">
                    <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                    </svg>
                  </div>
                  <div className="p-4 rounded-xl border-2 border-success bg-success/10 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-semibold text-success">Workflow Complete</span>
                    </div>
                    <p className="text-xs text-text-muted mt-1">
                      Total execution: {totalDuration}ms
                    </p>
                  </div>
                </>
              )}
            </div>
          </Card>
        </div>

        {/* Node Output Viewer */}
        <div className="col-span-7">
          <Card variant="default" padding="none" className="h-full">
            <div className="p-4 border-b border-border-subtle bg-bg-tertiary/50">
              <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider">
                {selectedNode ? `Output: ${selectedNode.name}` : 'Select a completed node to view output'}
              </h4>
            </div>
            <div className="p-4 max-h-[500px] overflow-auto">
              {selectedNode?.output ? (
                <JsonDisplay data={selectedNode.output} maxHeight="450px" />
              ) : (
                <div className="text-center py-16">
                  <div className="w-12 h-12 rounded-xl bg-bg-tertiary mx-auto mb-4 flex items-center justify-center">
                    <svg className="w-6 h-6 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                    </svg>
                  </div>
                  <p className="text-text-muted">
                    {isRunning ? 'Workflow in progress...' : 'Run the workflow to see node outputs'}
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Final Result Summary */}
      {finalResult && (
        <Card variant="elevated" className="border-success/30 animate-fade-in-up">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-success/20 flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-success">Workflow Completed Successfully</h3>
              <p className="text-sm text-text-secondary mt-1">
                {selectedWorkflow.name} executed {nodes.length} steps in {totalDuration}ms
              </p>
              <div className="mt-4">
                <JsonDisplay data={finalResult} title="Final Output" collapsible maxHeight="300px" />
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
