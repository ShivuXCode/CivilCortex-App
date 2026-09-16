export const mockInspectorUser = {
  id: 'user-inspector-1',
  email: 'inspector@civilcortex.com',
  role: 'INSPECTOR',
  organization_id: 'org-1'
};

export const mockEngineerUser = {
  id: 'user-engineer-1',
  email: 'engineer@civilcortex.com',
  role: 'ENGINEER',
  organization_id: 'org-1'
};

export const mockAdminUser = {
  id: 'user-admin-1',
  email: 'admin@civilcortex.com',
  role: 'ADMIN',
  organization_id: 'org-1'
};

export const mockBuilding = {
  id: 'b1',
  name: 'Test Building',
  location: '123 Test St',
  owner_id: 'user-admin-1',
  organization_id: 'org-1',
  floors: [
    {
      id: 'f1',
      level: 1,
      name: 'Ground Floor',
      building_id: 'b1',
      areas: [
        {
          id: 'a1',
          name: 'Lobby',
          floor_id: 'f1',
          structural_elements: [
            {
              id: 'se1',
              name: 'Main Pillar',
              element_type: 'COLUMN',
              area_id: 'a1'
            }
          ]
        }
      ]
    }
  ]
};

export const mockInspection = {
  id: 'insp-1',
  building_id: 'b1',
  inspector_id: 'user-inspector-1',
  status: 'IN_PROGRESS'
};

export const mockJobQueued = {
  job_id: 'job-1',
  status: 'QUEUED'
};

export const mockJobProcessing = {
  job_id: 'job-1',
  status: 'PROCESSING'
};

export const mockJobCompleted = {
  job_id: 'job-1',
  status: 'COMPLETED'
};

export const mockJobFailed = {
  job_id: 'job-1',
  status: 'FAILED',
  error_message: 'Image processing failed due to bad resolution'
};

export const mockAssessment = {
  id: 'assess-1',
  observation_id: 'obs-1',
  severity: 'HIGH',
  risk: 'REQUIRES_ENGINEER_REVIEW',
  repair_recommendation: 'Immediate shoring recommended',
  created_at: '2023-10-01T00:00:00Z',
  updated_at: '2023-10-01T00:00:00Z'
};

export const mockReport = {
  status: 'COMPLETED',
  content: '# Executive Report\n\nThis is the markdown content.\n\n## Findings\n- Severe cracking found in main pillar.',
  generated_at: '2023-10-01T00:05:00Z'
};
