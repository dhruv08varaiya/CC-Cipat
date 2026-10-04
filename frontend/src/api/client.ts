import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

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

export const fetchWorkloads = async (): Promise<WorkloadItem[]> => {
  const res = await api.get<WorkloadItem[]>('/simulation/workloads');
  return res.data;
};

export const fetchConfig = async (): Promise<any> => {
  const res = await api.get('/simulation/config');
  return res.data;
};

export const runSimulation = async (payload: {
  architecture: string;
  workload_id: string;
  seed?: number;
  max_events?: number;
  autoscaling_enabled?: boolean;
}): Promise<SimulationResult> => {
  const res = await api.post<SimulationResult>('/simulation/run', payload);
  return res.data;
};

export const fetchExperimentsList = async () => {
  const res = await api.get('/experiments/list');
  return res.data;
};

export const fetchExperimentSummary = async (expId: string) => {
  const res = await api.get(`/experiments/summary/${expId}`);
  return res.data;
};

export const runE4Experiment = async (payload: { seed?: number; max_events?: number }) => {
  const res = await api.post('/experiments/e4/run', payload);
  return res.data;
};

export const runE7Experiment = async (payload: { seed?: number; max_events?: number }) => {
  const res = await api.post('/experiments/e7/run', payload);
  return res.data;
};

export const fetchDatasetsList = async () => {
  const res = await api.get('/datasets/list');
  return res.data;
};

export const fetchDatasetStatistics = async () => {
  const res = await api.get('/datasets/statistics');
  return res.data;
};

export const fetchDatasetPreview = async (tableName: string, page = 1, pageSize = 20) => {
  const res = await api.get(`/datasets/preview/${tableName}?page=${page}&page_size=${pageSize}`);
  return res.data;
};

export const fetchSecurityRules = async () => {
  const res = await api.get('/security/rules');
  return res.data;
};

export const fetchRiskRegister = async () => {
  const res = await api.get('/security/risk-register');
  return res.data;
};

export const classifyPayload = async (serviceType: string, payload: Record<string, any>) => {
  const res = await api.post('/security/classify', { service_type: serviceType, payload });
  return res.data;
};

export default api;
