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

export const analyzeImage = async (inspectionId: string, imageId: string): Promise<AnalysisResult> => {
  const response = await apiClient.post(`/inspections/${inspectionId}/images/${imageId}/analyze`);
  return response.data;
};
