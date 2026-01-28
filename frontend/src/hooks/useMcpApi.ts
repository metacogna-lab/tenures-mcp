import { useState, useCallback } from 'react';
import type { ToolResponse, WorkflowResponse, HealthStatus, ReadyStatus } from '../types';

const API_BASE = '/api';
const AUTH_TOKEN = 'dev-token-insecure';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useMcpApi() {
  const [toolState, setToolState] = useState<ApiState<ToolResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const [workflowState, setWorkflowState] = useState<ApiState<WorkflowResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const [healthState, setHealthState] = useState<ApiState<HealthStatus>>({
    data: null,
    loading: false,
    error: null,
  });

  const [readyState, setReadyState] = useState<ApiState<ReadyStatus>>({
    data: null,
    loading: false,
    error: null,
  });

  const [resourceState, setResourceState] = useState<ApiState<Record<string, unknown>>>({
    data: null,
    loading: false,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    setHealthState({ data: null, loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/healthz`);
      const data = await res.json();
      setHealthState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setHealthState({ data: null, loading: false, error: String(err) });
      return null;
    }
  }, []);

  const checkReady = useCallback(async () => {
    setReadyState({ data: null, loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/ready`);
      const data = await res.json();
      setReadyState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setReadyState({ data: null, loading: false, error: String(err) });
      return null;
    }
  }, []);

  const executeTool = useCallback(async (toolName: string, inputData: Record<string, unknown>) => {
    setToolState({ data: null, loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/v1/tools/${toolName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${AUTH_TOKEN}`,
        },
        body: JSON.stringify({
          tool_name: toolName,
          context: {
            user_id: 'demo_user',
            tenant_id: 'demo_tenant',
            auth_context: 'demo_token',
            role: 'agent',
          },
          input_data: inputData,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Tool execution failed');
      }
      setToolState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : String(err);
      setToolState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const executeWorkflow = useCallback(async (workflowName: string, inputData: Record<string, unknown>) => {
    setWorkflowState({ data: null, loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/v1/workflows/${workflowName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${AUTH_TOKEN}`,
          'X-User-ID': 'demo_user',
          'X-Tenant-ID': 'demo_tenant',
          'X-Auth-Context': 'demo_token',
          'X-Role': 'agent',
        },
        body: JSON.stringify(inputData),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Workflow execution failed');
      }
      setWorkflowState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : String(err);
      setWorkflowState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  const fetchResource = useCallback(async (resourcePath: string) => {
    setResourceState({ data: null, loading: true, error: null });
    try {
      const res = await fetch(`${API_BASE}/v1/resources/${resourcePath}`, {
        headers: {
          'Authorization': `Bearer ${AUTH_TOKEN}`,
          'X-User-ID': 'demo_user',
          'X-Tenant-ID': 'demo_tenant',
          'X-Auth-Context': 'demo_token',
          'X-Role': 'agent',
        },
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Resource fetch failed');
      }
      setResourceState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const error = err instanceof Error ? err.message : String(err);
      setResourceState({ data: null, loading: false, error });
      return null;
    }
  }, []);

  return {
    toolState,
    workflowState,
    healthState,
    readyState,
    resourceState,
    checkHealth,
    checkReady,
    executeTool,
    executeWorkflow,
    fetchResource,
  };
}
