/**
 * TypeScript interfaces aligned with mcp/schemas (tools.py, base.py) and docs/schemas.md.
 * Used for tool/workflow inputs and outputs and client-side validation.
 */

/** Request context for MCP API calls. */
export interface RequestContext {
  user_id: string;
  tenant_id: string;
  auth_context: string;
  ip_address?: string;
  role: 'agent' | 'admin';
}

/** Tool execution request body. */
export interface ToolExecutionRequest {
  context: RequestContext;
  correlation_id?: string;
  tool_name: string;
  input_data: Record<string, unknown>;
}

/** Tool inputs (aligned with mcp/schemas/tools.py). */
export interface AnalyzeFeedbackInput {
  property_id: string;
  version?: string;
}

export interface CalculateBreachInput {
  tenancy_id: string;
  version?: string;
}

export interface GenerateVendorReportInput {
  property_id: string;
  version?: string;
}

export interface PrepareBreachNoticeInput {
  tenancy_id: string;
  breach_type: 'rent_arrears' | 'lease_violation' | 'property_damage';
  version?: string;
}

export interface OCRDocumentInput {
  document_url: string;
  version?: string;
}

export interface ExtractExpiryInput {
  text: string;
  version?: string;
}

/** Workflow body (property_id or tenancy_id). */
export interface WorkflowExecutionBody {
  property_id?: string;
  tenancy_id?: string;
}

/** Output types (shapes for display). */
export interface SentimentCategory {
  category: string;
  count: number;
  percentage: number;
}

export interface AnalyzeFeedbackOutput {
  property_id: string;
  total_feedback_count: number;
  sentiment_categories: SentimentCategory[];
  top_comments: string[];
  version?: string;
}

export interface BreachRisk {
  level: string;
  days_overdue?: number;
  breach_legal_status: string;
  recommended_action?: string;
}

export interface CalculateBreachOutput {
  tenancy_id: string;
  breach_risk: BreachRisk;
  current_balance?: number;
  last_payment_date?: string;
  version?: string;
}

export interface GenerateVendorReportOutput {
  property_id: string;
  report_date: string;
  feedback_summary: Record<string, unknown>;
  market_trends?: Record<string, unknown>;
  recommendations: string[];
  version?: string;
}

export interface PrepareBreachNoticeOutput {
  notice_id: string;
  tenancy_id: string;
  breach_type: string;
  draft_content: string;
  status: string;
  created_at: string;
  version?: string;
}

export interface OCRDocumentOutput {
  document_url: string;
  extracted_text: string;
  confidence_score?: number;
  page_count?: number;
  version?: string;
}

export interface ExtractedDate {
  field_name: string;
  date_value: string;
  confidence: number;
}

export interface ExtractExpiryOutput {
  extracted_dates: ExtractedDate[];
  version?: string;
}
