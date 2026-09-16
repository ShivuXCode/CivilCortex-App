import { apiClient } from './client';

export interface Inspection {
  id: string;
  notes?: string;
  building_id: string;
  inspector_id: string;
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
