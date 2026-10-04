// Native fetch wrapper — zero dependency
const request = async <T>(path: string, options?: RequestInit): Promise<T> => {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const errorText = await res.text();
    try {
      const errJson = JSON.parse(errorText);
      throw new Error(errJson.detail || res.statusText);
    } catch (e: any) {
      throw new Error(e.message || errorText || res.statusText);
    }
  }
  return res.json();
};

export interface WorkloadItem {
  id: string;
  name: string;
  description: string;
  nominal_rate_rps: number;
  duration_seconds: number;
  burst_config?: Record<string, any>;
  failure_metadata?: Record<string, any>;
}

export interface SimulationResult {
  status: string;
  architecture: string;
  workload_id: string;
  results: {
    summary?: {
      total_requests: number;
      completed_requests: number;
      dropped_requests: number;
      avg_latency_ms: number;
      p95_latency_ms: number;
      p99_latency_ms: number;
      avg_queue_length: number;
      max_queue_length: number;
      avg_utilization: number;
      peak_utilization: number;
    };
    time_series?: Array<{
      time_sec: number;
      arrival_rate: number;
      completed_rate: number;
      queue_length: number;
      utilization: number;
      latency_ms: number;
      active_instances?: number;
    }>;
    scaling_events?: Array<{
      timestamp: number;
      event_type: string;
      prev_instances: number;
      new_instances: number;
      reason: string;
    }>;
  };
}

export const fetchWorkloads = () => request<WorkloadItem[]>('/simulation/workloads');
export const fetchConfig = () => request<any>('/simulation/config');
export const runSimulation = (payload: {
  architecture: string;
  workload_id: string;
  seed?: number;
  max_events?: number;
  autoscaling_enabled?: boolean;
}) => request<SimulationResult>('/simulation/run', { method: 'POST', body: JSON.stringify(payload) });

export const fetchExperimentsList = () => request<any[]>('/experiments/list');
export const fetchExperimentSummary = (expId: string) => request<any>(`/experiments/summary/${expId}`);
export const runE4Experiment = (payload: { seed?: number; max_events?: number }) =>
  request<any>('/experiments/e4/run', { method: 'POST', body: JSON.stringify(payload) });
export const runE7Experiment = (payload: { seed?: number; max_events?: number }) =>
  request<any>('/experiments/e7/run', { method: 'POST', body: JSON.stringify(payload) });

export const fetchDatasetsList = () => request<any[]>('/datasets/list');
export const fetchDatasetStatistics = () => request<any>('/datasets/statistics');
export const fetchDatasetPreview = (tableName: string, page = 1, pageSize = 20) =>
  request<any>(`/datasets/preview/${tableName}?page=${page}&page_size=${pageSize}`);

export const fetchSecurityRules = () => request<any>('/security/rules');
export const fetchRiskRegister = () => request<any>('/security/risk-register');
export const classifyPayload = (serviceType: string, payload: Record<string, any>) =>
  request<any>('/security/classify', { method: 'POST', body: JSON.stringify({ service_type: serviceType, payload }) });
