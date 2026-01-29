/**
 * Client-side validators aligned with docs/schemas.md Validation Rules and mcp/schemas.
 * Use before calling MCP; do not submit if validation fails.
 */

import { z } from 'zod';

const ID_PATTERN = /^[a-zA-Z0-9_-]+$/;
const ID_MIN = 1;
const ID_MAX = 100;

/** property_id and tenancy_id: alphanumeric, hyphen, underscore; 1-100 chars. */
export const propertyIdSchema = z
  .string()
  .min(ID_MIN, 'Property ID is required')
  .max(ID_MAX, `Property ID must be at most ${ID_MAX} characters`)
  .regex(ID_PATTERN, 'Property ID may only contain letters, numbers, hyphens, and underscores');

export const tenancyIdSchema = z
  .string()
  .min(ID_MIN, 'Tenancy ID is required')
  .max(ID_MAX, `Tenancy ID must be at most ${ID_MAX} characters`)
  .regex(ID_PATTERN, 'Tenancy ID may only contain letters, numbers, hyphens, and underscores');

/** file_id: alphanumeric, hyphen, underscore; 1-100 chars. */
export const fileIdSchema = z
  .string()
  .min(ID_MIN, 'File ID is required')
  .max(ID_MAX, `File ID must be at most ${ID_MAX} characters`)
  .regex(ID_PATTERN, 'File ID may only contain letters, numbers, hyphens, and underscores');

/** document_url: must start with http://, https://, or vault:// */
export const documentUrlSchema = z
  .string()
  .min(1, 'Document URL is required')
  .refine(
    (v) => v.startsWith('http://') || v.startsWith('https://') || v.startsWith('vault://'),
    'Document URL must start with http://, https://, or vault://'
  );

/** breach_type: rent_arrears | lease_violation | property_damage */
export const breachTypeSchema = z.enum(['rent_arrears', 'lease_violation', 'property_damage']);

/** text for extract_expiry_date: 10-10000 chars */
export const extractExpiryTextSchema = z
  .string()
  .min(10, 'Text must be at least 10 characters')
  .max(10000, 'Text must be at most 10000 characters');

/** role: agent | admin */
export const roleSchema = z.enum(['agent', 'admin']);

/** collection_scope: valid integration names */
export const collectionScopeSchema = z.array(
  z.enum(['gmail', 'drive', 'vaultre', 'ailo'])
).default(['gmail', 'drive', 'vaultre', 'ailo']);

// =============================================================================
// Existing Tool Input Schemas
// =============================================================================

export const analyzeFeedbackInputSchema = z.object({
  property_id: propertyIdSchema,
});

export const calculateBreachInputSchema = z.object({
  tenancy_id: tenancyIdSchema,
});

export const generateVendorReportInputSchema = z.object({
  property_id: propertyIdSchema,
});

export const prepareBreachNoticeInputSchema = z.object({
  tenancy_id: tenancyIdSchema,
  breach_type: breachTypeSchema,
});

export const ocrDocumentInputSchema = z.object({
  document_url: documentUrlSchema,
});

export const extractExpiryInputSchema = z.object({
  text: extractExpiryTextSchema,
});

// =============================================================================
// Integration Tool Input Schemas
// =============================================================================

/** Gmail: Fetch emails related to a property. */
export const fetchPropertyEmailsInputSchema = z.object({
  property_id: propertyIdSchema,
  days_back: z.number().min(1).max(365).default(30),
});

/** Gmail: Search communication threads. */
export const searchCommunicationThreadsInputSchema = z.object({
  query: z.string().min(1, 'Query is required').max(500, 'Query must be at most 500 characters'),
  contact_email: z.string().email('Invalid email format').optional().nullable(),
  max_results: z.number().min(1).max(50).default(10),
});

/** Google Drive: List property documents. */
export const listPropertyDocumentsInputSchema = z.object({
  property_id: propertyIdSchema,
});

/** Google Drive: Get document content. */
export const getDocumentContentInputSchema = z.object({
  file_id: fileIdSchema,
});

/** Google Drive: Check document expiries. */
export const checkDocumentExpiryInputSchema = z.object({
  property_id: propertyIdSchema,
  days_ahead: z.number().min(1).max(365).default(30),
});

/** VaultRE: List active properties. */
export const listActivePropertiesInputSchema = z.object({
  status: z.string().optional().nullable(),
  limit: z.number().min(1).max(100).default(20),
});

/** VaultRE: Get property contacts. */
export const getPropertyContactsInputSchema = z.object({
  property_id: propertyIdSchema,
});

/** VaultRE: Get upcoming open homes. */
export const getUpcomingOpenHomesInputSchema = z.object({
  days_ahead: z.number().min(1).max(30).default(7),
});

/** Ailo: List tenancies in arrears. */
export const listArrearsTenanciesInputSchema = z.object({
  min_days: z.number().min(1).default(1),
  max_results: z.number().min(1).max(100).default(20),
});

/** Ailo: Get tenant communication history. */
export const getTenantCommunicationHistoryInputSchema = z.object({
  tenancy_id: tenancyIdSchema,
  limit: z.number().min(1).max(100).default(20),
});

// =============================================================================
// Workflow Body Schemas
// =============================================================================

export const workflowPropertyIdSchema = z.object({
  property_id: propertyIdSchema,
});

export const workflowTenancyIdSchema = z.object({
  tenancy_id: tenancyIdSchema,
});

/** Unified collection workflow input. */
export const unifiedCollectionWorkflowInputSchema = z.object({
  property_id: propertyIdSchema,
  collection_scope: collectionScopeSchema,
});

// =============================================================================
// Tool Input Schema Map
// =============================================================================

/** Map tool name to Zod schema for validation. */
export const toolInputSchemas: Record<string, z.ZodType<Record<string, unknown>>> = {
  // Existing tools
  analyze_open_home_feedback: analyzeFeedbackInputSchema,
  calculate_breach_status: calculateBreachInputSchema,
  generate_vendor_report: generateVendorReportInputSchema,
  prepare_breach_notice: prepareBreachNoticeInputSchema,
  ocr_document: ocrDocumentInputSchema,
  extract_expiry_date: extractExpiryInputSchema,
  // Gmail tools
  fetch_property_emails: fetchPropertyEmailsInputSchema,
  search_communication_threads: searchCommunicationThreadsInputSchema,
  // Google Drive tools
  list_property_documents: listPropertyDocumentsInputSchema,
  get_document_content: getDocumentContentInputSchema,
  check_document_expiry: checkDocumentExpiryInputSchema,
  // VaultRE tools
  list_active_properties: listActivePropertiesInputSchema,
  get_property_contacts: getPropertyContactsInputSchema,
  get_upcoming_open_homes: getUpcomingOpenHomesInputSchema,
  // Ailo tools
  list_arrears_tenancies: listArrearsTenanciesInputSchema,
  get_tenant_communication_history: getTenantCommunicationHistoryInputSchema,
};

/**
 * Validate tool input; returns { success: true, data } or { success: false, errors }.
 */
export function validateToolInput(
  toolName: string,
  input: Record<string, unknown>
): { success: true; data: Record<string, unknown> } | { success: false; errors: string[] } {
  const schema = toolInputSchemas[toolName];
  if (!schema) {
    return { success: false, errors: [`Unknown tool: ${toolName}`] };
  }
  const result = schema.safeParse(input);
  if (result.success) {
    return { success: true, data: result.data as Record<string, unknown> };
  }
  const errors = result.error.flatten().fieldErrors;
  const messages = Object.entries(errors).flatMap(([field, msgs]) =>
    (msgs ?? []).map((m) => `${field}: ${m}`)
  );
  return { success: false, errors: messages };
}

/**
 * Validate workflow body (property_id or tenancy_id).
 */
export function validateWorkflowInput(
  workflowName: string,
  input: Record<string, unknown>
): { success: true; data: Record<string, unknown> } | { success: false; errors: string[] } {
  if (workflowName === 'weekly_vendor_report' || workflowName === 'compliance_audit') {
    const result = workflowPropertyIdSchema.safeParse(input);
    if (result.success) return { success: true, data: result.data as Record<string, unknown> };
    const messages = (result.error.flatten().fieldErrors.property_id ?? []).map((m) => `property_id: ${m}`);
    return { success: false, errors: messages };
  }
  if (workflowName === 'arrears_detection') {
    const result = workflowTenancyIdSchema.safeParse(input);
    if (result.success) return { success: true, data: result.data as Record<string, unknown> };
    const messages = (result.error.flatten().fieldErrors.tenancy_id ?? []).map((m) => `tenancy_id: ${m}`);
    return { success: false, errors: messages };
  }
  if (workflowName === 'unified_collection') {
    const result = unifiedCollectionWorkflowInputSchema.safeParse(input);
    if (result.success) return { success: true, data: result.data as Record<string, unknown> };
    const errors = result.error.flatten().fieldErrors;
    const messages = Object.entries(errors).flatMap(([field, msgs]) =>
      (msgs ?? []).map((m) => `${field}: ${m}`)
    );
    return { success: false, errors: messages };
  }
  return { success: false, errors: [`Unknown workflow: ${workflowName}`] };
}
