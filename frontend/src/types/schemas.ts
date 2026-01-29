/**
 * TypeScript interfaces aligned with mcp/schemas (tools.py, base.py) and docs/schemas.md.
 * Used for tool/workflow inputs and outputs and client-side validation.
 *
 * Types are auto-generated from OpenAPI spec - run `npm run generate:types` to update.
 */

import type { components } from './generated/api';

// Convenience type aliases for accessing nested schema types
export type Schemas = components['schemas'];

// =============================================================================
// Core Schemas
// =============================================================================
export type RequestContext = Schemas['RequestContext'];
export type ToolExecutionRequest = Schemas['ToolExecutionRequest'];
export type ToolExecutionResponse = Schemas['ToolExecutionResponse'];
export type ErrorResponse = Schemas['ErrorResponse'];
export type ResourceResponse = Schemas['ResourceResponse'];
export type HealthResponse = Schemas['HealthResponse'];
export type ReadinessResponse = Schemas['ReadinessResponse'];
export type VersionResponse = Schemas['VersionResponse'];

// =============================================================================
// Tool Input Schemas (Existing)
// =============================================================================
export type AnalyzeFeedbackInput = Schemas['AnalyzeFeedbackInput'];
export type CalculateBreachInput = Schemas['CalculateBreachInput'];
export type GenerateVendorReportInput = Schemas['GenerateVendorReportInput'];
export type PrepareBreachNoticeInput = Schemas['PrepareBreachNoticeInput'];
export type OCRDocumentInput = Schemas['OCRDocumentInput'];
export type ExtractExpiryInput = Schemas['ExtractExpiryInput'];

// =============================================================================
// Tool Output Schemas (Existing)
// =============================================================================
export type AnalyzeFeedbackOutput = Schemas['AnalyzeFeedbackOutput'];
export type CalculateBreachOutput = Schemas['CalculateBreachOutput'];
export type GenerateVendorReportOutput = Schemas['GenerateVendorReportOutput'];
export type PrepareBreachNoticeOutput = Schemas['PrepareBreachNoticeOutput'];
export type OCRDocumentOutput = Schemas['OCRDocumentOutput'];
export type ExtractExpiryOutput = Schemas['ExtractExpiryOutput'];
export type SentimentCategory = Schemas['SentimentCategory'];
export type BreachRisk = Schemas['BreachRisk'];
export type ExtractedDate = Schemas['ExtractedDate'];

// =============================================================================
// Workflow Input Schemas
// =============================================================================
export type VendorReportWorkflowInput = Schemas['VendorReportWorkflowInput'];
export type ArrearsDetectionWorkflowInput = Schemas['ArrearsDetectionWorkflowInput'];
export type ComplianceAuditWorkflowInput = Schemas['ComplianceAuditWorkflowInput'];
export type UnifiedCollectionWorkflowInput = Schemas['UnifiedCollectionWorkflowInput'];

// =============================================================================
// Integration Enums
// =============================================================================
export type PropertyClass = Schemas['PropertyClass'];
export type PropertyStatus = Schemas['PropertyStatus'];
export type ContactType = Schemas['ContactType'];
export type RentFrequency = Schemas['RentFrequency'];
export type ArrearsStatus = Schemas['ArrearsStatus'];
export type GmailLabelType = Schemas['GmailLabelType'];
export type DriveMimeType = Schemas['DriveMimeType'];

// =============================================================================
// Integration Tool Input Schemas
// =============================================================================
export type FetchPropertyEmailsInput = Schemas['FetchPropertyEmailsInput'];
export type SearchCommunicationThreadsInput = Schemas['SearchCommunicationThreadsInput'];
export type ListPropertyDocumentsInput = Schemas['ListPropertyDocumentsInput'];
export type GetDocumentContentInput = Schemas['GetDocumentContentInput'];
export type CheckDocumentExpiryInput = Schemas['CheckDocumentExpiryInput'];
export type ListActivePropertiesInput = Schemas['ListActivePropertiesInput'];
export type GetPropertyContactsInput = Schemas['GetPropertyContactsInput'];
export type GetUpcomingOpenHomesInput = Schemas['GetUpcomingOpenHomesInput'];
export type ListArrearsTenanciesInput = Schemas['ListArrearsTenanciesInput'];
export type GetTenantCommunicationHistoryInput = Schemas['GetTenantCommunicationHistoryInput'];

// =============================================================================
// Integration Tool Output Schemas
// =============================================================================
export type FetchPropertyEmailsOutput = Schemas['FetchPropertyEmailsOutput'];
export type SearchCommunicationThreadsOutput = Schemas['SearchCommunicationThreadsOutput'];
export type ListPropertyDocumentsOutput = Schemas['ListPropertyDocumentsOutput'];
export type GetDocumentContentOutput = Schemas['GetDocumentContentOutput'];
export type CheckDocumentExpiryOutput = Schemas['CheckDocumentExpiryOutput'];
export type ListActivePropertiesOutput = Schemas['ListActivePropertiesOutput'];
export type GetPropertyContactsOutput = Schemas['GetPropertyContactsOutput'];
export type GetUpcomingOpenHomesOutput = Schemas['GetUpcomingOpenHomesOutput'];
export type ListArrearsTenanciesOutput = Schemas['ListArrearsTenanciesOutput'];
export type GetTenantCommunicationHistoryOutput = Schemas['GetTenantCommunicationHistoryOutput'];

// =============================================================================
// Supporting Schemas
// =============================================================================
export type EmailSummary = Schemas['EmailSummary'];
export type ThreadSummary = Schemas['ThreadSummary'];
export type DocumentInfo = Schemas['DocumentInfo'];
export type ExpiryAlert = Schemas['ExpiryAlert'];
export type PropertySummary = Schemas['PropertySummary'];
export type VaultREContact = Schemas['VaultREContact'];
export type PropertyContacts = Schemas['PropertyContacts'];
export type OpenHomeSummary = Schemas['OpenHomeSummary'];
export type AiloLedgerSummary = Schemas['AiloLedgerSummary'];
export type ArrearsReport = Schemas['ArrearsReport'];
export type CommunicationEntry = Schemas['CommunicationEntry'];
export type CommunicationHistory = Schemas['CommunicationHistory'];

// =============================================================================
// Resource Schemas
// =============================================================================
export type PropertyDetails = Schemas['PropertyDetails'];
export type PropertyFeedback = Schemas['PropertyFeedback'];
export type FeedbackEntry = Schemas['FeedbackEntry'];
export type LedgerSummary = Schemas['LedgerSummary'];
export type PropertyDocuments = Schemas['PropertyDocuments'];
export type DocumentEntry = Schemas['DocumentEntry'];

// =============================================================================
// Agent Manifest
// =============================================================================
export type AgentManifest = Schemas['AgentManifest'];

// Tool name union type for type-safe tool selection
export type ToolName =
  | 'analyze_open_home_feedback'
  | 'calculate_breach_status'
  | 'ocr_document'
  | 'extract_expiry_date'
  | 'generate_vendor_report'
  | 'prepare_breach_notice'
  // Integration tools
  | 'fetch_property_emails'
  | 'search_communication_threads'
  | 'list_property_documents'
  | 'get_document_content'
  | 'check_document_expiry'
  | 'list_active_properties'
  | 'get_property_contacts'
  | 'get_upcoming_open_homes'
  | 'list_arrears_tenancies'
  | 'get_tenant_communication_history';

// Workflow name union type
export type WorkflowName =
  | 'weekly_vendor_report'
  | 'arrears_detection'
  | 'compliance_audit'
  | 'unified_collection';

// Collection scope options for unified collection workflow
export type CollectionScope = 'gmail' | 'drive' | 'vaultre' | 'ailo';

/** Workflow body (property_id or tenancy_id). */
export interface WorkflowExecutionBody {
  property_id?: string;
  tenancy_id?: string;
  collection_scope?: CollectionScope[];
}

// Tool input type mapping for type-safe tool execution
export interface ToolInputMap {
  analyze_open_home_feedback: Schemas['AnalyzeFeedbackInput'];
  calculate_breach_status: Schemas['CalculateBreachInput'];
  ocr_document: Schemas['OCRDocumentInput'];
  extract_expiry_date: Schemas['ExtractExpiryInput'];
  generate_vendor_report: Schemas['GenerateVendorReportInput'];
  prepare_breach_notice: Schemas['PrepareBreachNoticeInput'];
  fetch_property_emails: Schemas['FetchPropertyEmailsInput'];
  search_communication_threads: Schemas['SearchCommunicationThreadsInput'];
  list_property_documents: Schemas['ListPropertyDocumentsInput'];
  get_document_content: Schemas['GetDocumentContentInput'];
  check_document_expiry: Schemas['CheckDocumentExpiryInput'];
  list_active_properties: Schemas['ListActivePropertiesInput'];
  get_property_contacts: Schemas['GetPropertyContactsInput'];
  get_upcoming_open_homes: Schemas['GetUpcomingOpenHomesInput'];
  list_arrears_tenancies: Schemas['ListArrearsTenanciesInput'];
  get_tenant_communication_history: Schemas['GetTenantCommunicationHistoryInput'];
}

// Tool output type mapping for type-safe tool execution
export interface ToolOutputMap {
  analyze_open_home_feedback: Schemas['AnalyzeFeedbackOutput'];
  calculate_breach_status: Schemas['CalculateBreachOutput'];
  ocr_document: Schemas['OCRDocumentOutput'];
  extract_expiry_date: Schemas['ExtractExpiryOutput'];
  generate_vendor_report: Schemas['GenerateVendorReportOutput'];
  prepare_breach_notice: Schemas['PrepareBreachNoticeOutput'];
  fetch_property_emails: Schemas['FetchPropertyEmailsOutput'];
  search_communication_threads: Schemas['SearchCommunicationThreadsOutput'];
  list_property_documents: Schemas['ListPropertyDocumentsOutput'];
  get_document_content: Schemas['GetDocumentContentOutput'];
  check_document_expiry: Schemas['CheckDocumentExpiryOutput'];
  list_active_properties: Schemas['ListActivePropertiesOutput'];
  get_property_contacts: Schemas['GetPropertyContactsOutput'];
  get_upcoming_open_homes: Schemas['GetUpcomingOpenHomesOutput'];
  list_arrears_tenancies: Schemas['ListArrearsTenanciesOutput'];
  get_tenant_communication_history: Schemas['GetTenantCommunicationHistoryOutput'];
}
