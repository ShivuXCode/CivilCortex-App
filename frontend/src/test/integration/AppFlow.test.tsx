
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
import App from '../../App';
import { render } from '@testing-library/react';
import * as authApi from '../../api/auth';
import * as hierarchyApi from '../../api/hierarchy';
import * as inspectionsApi from '../../api/inspections';
import * as analysisApi from '../../api/analysis';
import { 
  mockInspectorUser, 
  mockBuilding, 
  mockInspection, 
  mockJobQueued, 
  mockJobProcessing, 
  mockJobCompleted, 
  mockAssessment, 
  mockReport 
} from '../fixtures';

vi.mock('../../api/auth');
vi.mock('../../api/hierarchy');
vi.mock('../../api/inspections');
vi.mock('../../api/analysis');

describe('Full Application Flow (Integration)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('completes the full inspection lifecycle', async () => {
    // 1. Setup global mocks
    (authApi.login as Mock).mockResolvedValue({
      access_token: 'fake',
      token_type: 'bearer',
      user: mockInspectorUser
    });
    
    (authApi.getMe as Mock).mockResolvedValue(mockInspectorUser);
    
    (hierarchyApi.getBuildings as Mock).mockResolvedValue([mockBuilding]);
    (hierarchyApi.getBuilding as Mock).mockResolvedValue(mockBuilding);
    
    (inspectionsApi.createInspection as Mock).mockResolvedValue(mockInspection);
    (inspectionsApi.uploadInspectionImage as Mock).mockResolvedValue({ id: 'img1', object_key: 'obj1' });
    (inspectionsApi.analyzeImage as Mock).mockResolvedValue(mockJobQueued);
    
    (analysisApi.getAnalysisJob as Mock)
      .mockResolvedValueOnce(mockJobProcessing)
      .mockResolvedValueOnce(mockJobCompleted);
      
    (inspectionsApi.getAssessment as Mock).mockResolvedValue([mockAssessment]);
    (inspectionsApi.getReport as Mock).mockResolvedValue(mockReport);

    // 2. Render App (Starting at Login)
    render(<App />);
    
    // 3. Login
    fireEvent.change(screen.getByPlaceholderText(/engineer@civilcortex.com/i), { target: { value: 'inspector@civilcortex.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // 4. Wait for Dashboard routing
    await waitFor(() => {
      expect(screen.getByText('Dashboard', { selector: 'h1' })).toBeInTheDocument();
    });

    // 5. Navigate to New Inspection
    fireEvent.click(screen.getByRole('button', { name: /new inspection/i }));
    
    // 6. Hierarchy Selection
    await waitFor(() => screen.getByRole('combobox', { name: /building/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /building/i }), { target: { value: 'b1' } });
    await waitFor(() => screen.getByRole('combobox', { name: /floor/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /floor/i }), { target: { value: 'f1' } });
    await waitFor(() => screen.getByRole('combobox', { name: /area/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /area/i }), { target: { value: 'a1' } });
    await waitFor(() => screen.getByRole('combobox', { name: /structural element/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /structural element/i }), { target: { value: 'se1' } });
    
    fireEvent.click(screen.getByRole('button', { name: /continue to image inspection/i }));

    // 7. Image Upload
    await waitFor(() => screen.getByText('2. Capture Defect'));
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['dummy'], 'crack.png', { type: 'image/png' });
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);
    
    // 8. Analyze
    await waitFor(() => screen.getByRole('button', { name: /analyze image/i }));
    fireEvent.click(screen.getByRole('button', { name: /analyze image/i }));
    
    // 9. Polling steps
    await waitFor(() => {
      expect(screen.getByText('Analysis Queued...')).toBeInTheDocument();
    });
    
    // It mocks PROCESSING then COMPLETED
    await waitFor(() => {
      expect(screen.getByText('Analysis In Progress...')).toBeInTheDocument();
    }, { timeout: 4000 });
    
    await waitFor(() => {
      expect(screen.getByText('Analysis Completed')).toBeInTheDocument();
    }, { timeout: 4000 });

    // 10. Navigation to Report
    fireEvent.click(screen.getByRole('button', { name: /view engineering report/i }));
    
    await waitFor(() => {
      expect(screen.getByText('Engineering Assessment Report')).toBeInTheDocument();
      // Should show the mock report text
      expect(screen.getByText('Severe cracking found in main pillar.')).toBeInTheDocument();
    });
  });
});
