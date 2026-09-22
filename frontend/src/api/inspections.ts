import { apiClient } from './client';

export interface Inspection {
  id: string;
  notes?: string;
  building_id: string;
  inspector_id: string;
  assigned_engineer_id?: string;
  status: string;
  created_at: string;
}

export interface InspectionImage {
  id: string;
  inspection_id: string;
  original_filename: string;
  file_path: string;
  mime_type: string;
}

export interface AnalysisResult {
  defect_type: string;
  confidence: number;
  model_name: string;
  model_version: string;
  model_status: string;
}

export const getInspections = async (): Promise<Inspection[]> => {
  const response = await apiClient.get('/inspections/');
  return response.data;
};

export const createInspection = async (data: { building_id: string; notes?: string }): Promise<Inspection> => {
  const response = await apiClient.post('/inspections/', data);
  return response.data;
};

export const uploadInspectionImage = async (inspectionId: string, file: File): Promise<InspectionImage> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post(`/inspections/${inspectionId}/images`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export interface AnalyzeImageResponse {
  job_id: string;
  status: string;
  message: string;
}

export const analyzeImage = async (inspectionId: string, imageId: string): Promise<AnalyzeImageResponse> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/images/${imageId}/analyze`);
  return response.data;
};

export interface AssessmentResponse {
  id: string;
  observation_id: string;
  severity: string;
  risk: string;
  repair_recommendation?: string;
  rag_context?: string;
  created_at: string;
  updated_at: string;
}

export const getAssessment = async (inspectionId: string): Promise<AssessmentResponse[]> => {
  const response = await apiClient.get(`/inspections/${inspectionId}/assessment`);
  return response.data;
};

export interface ReportResponse {
  content: string;
  generated_at: string;
  status: string;
}

export const getReport = async (inspectionId: string): Promise<ReportResponse> => {
  const response = await apiClient.get(`/inspections/${inspectionId}/report`);
  return response.data;
};

export const submitInspection = async (inspectionId: string): Promise<{status: string}> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/submit`);
  return response.data;
};

export const assignEngineer = async (inspectionId: string, engineerId: string): Promise<{message: string}> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/assign`, { engineer_id: engineerId });
  return response.data;
};

export const beginReview = async (inspectionId: string): Promise<{status: string}> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/begin-review`);
  return response.data;
};

export const approveInspection = async (inspectionId: string): Promise<{status: string}> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/approve`);
  return response.data;
};

export const requestRevision = async (inspectionId: string, reason: string): Promise<{status: string}> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/request-revision`, { reason });
  return response.data;
};

export const generateReport = async (inspectionId: string): Promise<{status: string, message: string}> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/generate-report`);
  return response.data;
};
