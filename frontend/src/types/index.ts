export interface Tool {
  id: string;
  name: string;
  description: string;
  tier: 'A' | 'B' | 'C';
  requiresHitl?: boolean;
  inputSchema: {
    field: string;
    type: string;
    placeholder: string;
  };
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: string[];
  inputSchema: {
    field: string;
    type: string;
    placeholder: string;
  };
}

export interface Resource {
  uri: string;
  name: string;
  description: string;
  paramName: string;
  placeholder: string;
}

export interface HealthStatus {
  status: string;
  version: string;
}

export interface ReadyStatus {
  status: string;
  checks: {
    database: boolean;
    tools_registered: boolean;
    resources_registered: boolean;
  };
  version: string;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  correlation_id: string;
  data?: T;
  error?: string;
  execution_time_ms?: number;
}

export interface ToolResponse {
  success: boolean;
  correlation_id: string;
  tool_name: string;
  output_data: Record<string, unknown>;
  execution_time_ms: number;
  trace_id: string | null;
}

export interface WorkflowResponse {
  success: boolean;
  correlation_id: string;
  workflow_name: string;
  output: Record<string, unknown>;
}
