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

/** Tool input schemas (for forms). */
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

/** Workflow body schemas */
export const workflowPropertyIdSchema = z.object({
  property_id: propertyIdSchema,
});

export const workflowTenancyIdSchema = z.object({
  tenancy_id: tenancyIdSchema,
});

/** Map tool name to Zod schema for validation. */
export const toolInputSchemas: Record<string, z.ZodType<Record<string, unknown>>> = {
  analyze_open_home_feedback: analyzeFeedbackInputSchema,
  calculate_breach_status: calculateBreachInputSchema,
  generate_vendor_report: generateVendorReportInputSchema,
  prepare_breach_notice: prepareBreachNoticeInputSchema,
  ocr_document: ocrDocumentInputSchema,
  extract_expiry_date: extractExpiryInputSchema,
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
  return { success: false, errors: [`Unknown workflow: ${workflowName}`] };
}
