import { apiClient } from './client';

export interface Defect {
  id: string;
  defect_type: string;
  status: string;
  structural_element_id: string;
  created_at: string;
}

export interface CrackObservation {
  id: string;
  defect_id: string;
  inspection_id: string;
  image_id: string;
}

export interface Assessment {
  id: string;
  observation_id: string;
  severity: string;
  risk: string;
  repair_recommendation?: string;
  created_at: string;
  updated_at: string;
}

export const getDefects = async (): Promise<Defect[]> => {
  const response = await apiClient.get('/defects/');
  return response.data;
};

export const createDefect = async (data: { defect_type: string; structural_element_id: string }): Promise<Defect> => {
  const response = await apiClient.post('/defects/', data);
  return response.data;
};

export const createObservation = async (data: { defect_id: string; inspection_id: string; image_id: string }): Promise<CrackObservation> => {
  const response = await apiClient.post('/defects/observations', data);
  return response.data;
};

export const createAssessment = async (observationId: string, data: { severity: string; risk: string; repair_recommendation?: string }): Promise<Assessment> => {
  const response = await apiClient.post(`/defects/observations/${observationId}/assessments`, data);
  return response.data;
};

export const updateDefectStatus = async (defectId: string, status: string): Promise<Defect> => {
  const response = await apiClient.put(`/defects/${defectId}`, { status });
  return response.data;
};

export interface AssessmentUpdate {
  severity?: string;
  risk?: string;
  repair_recommendation?: string;
}

export const updateAssessment = async (assessmentId: string, data: AssessmentUpdate): Promise<Assessment> => {
  const response = await apiClient.patch(`/defects/assessments/${assessmentId}`, data);
  return response.data;
};
