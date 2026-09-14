import { apiClient } from './client';

export interface Building {
  id: string;
  name: string;
  location?: string;
  created_at: string;
  updated_at: string;
}

export interface Floor {
  id: string;
  building_id: string;
  name: string;
  level?: number;
}

export interface Area {
  id: string;
  floor_id: string;
  name: string;
}

export interface StructuralElement {
  id: string;
  area_id: string;
  name: string;
  element_type: string;
}

export interface StructuralElementDetail extends StructuralElement {}

export interface AreaDetail extends Area {
  structural_elements: StructuralElementDetail[];
}

export interface FloorDetail extends Floor {
  areas: AreaDetail[];
}

export interface BuildingDetail extends Building {
  floors: FloorDetail[];
}

export const getBuildings = async (): Promise<Building[]> => {
  const response = await apiClient.get('/buildings');
  return response.data;
};

export const getBuilding = async (id: string): Promise<BuildingDetail> => {
  const response = await apiClient.get(`/buildings/${id}`);
  return response.data;
};

export const createBuilding = async (data: { name: string; location?: string }): Promise<Building> => {
  const response = await apiClient.post('/buildings', data);
  return response.data;
};

export const createFloor = async (data: { name: string; building_id: string; level?: number }): Promise<Floor> => {
  const response = await apiClient.post('/floors', data);
  return response.data;
};

export const createArea = async (data: { name: string; floor_id: string }): Promise<Area> => {
  const response = await apiClient.post('/areas', data);
  return response.data;
};

export const createStructuralElement = async (data: { name: string; area_id: string; element_type: string }): Promise<StructuralElement> => {
  const response = await apiClient.post('/structural-elements', data);
  return response.data;
};
