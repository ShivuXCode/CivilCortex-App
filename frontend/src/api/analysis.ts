import { apiClient } from './client';

export interface AnalysisJobResponse {
  job_id: string;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}

export const getAnalysisJob = async (jobId: string): Promise<AnalysisJobResponse> => {
  const response = await apiClient.get(`/analysis/${jobId}`);
  return response.data;
};
