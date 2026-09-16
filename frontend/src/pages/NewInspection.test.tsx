
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, Mock } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { NewInspection } from './NewInspection';
import * as hierarchyApi from '../api/hierarchy';
import * as inspectionsApi from '../api/inspections';
import * as analysisApi from '../api/analysis';

// Mock dependencies
vi.mock('../api/hierarchy');
vi.mock('../api/inspections');
vi.mock('../api/analysis');

describe('NewInspection component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock buildings API
    (hierarchyApi.getBuildings as Mock).mockResolvedValue([
      { id: 'b1', name: 'Test Building', location: 'Test Location', owner_id: 'user1' }
    ]);
    
    // Mock building detail API
    (hierarchyApi.getBuilding as Mock).mockResolvedValue({
      id: 'b1', 
      name: 'Test Building', 
      location: 'Test Location', 
      owner_id: 'user1',
      floors: [
        {
          id: 'f1', name: 'Floor 1', level: 1, building_id: 'b1',
          areas: [
            {
              id: 'a1', name: 'Lobby', floor_id: 'f1',
              structural_elements: [
                { id: 'e1', name: 'Wall', element_type: 'Wall', area_id: 'a1' }
              ]
            }
          ]
        }
      ]
    });
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <NewInspection />
      </BrowserRouter>
    );
  };

  it('progresses from Step 1 to Step 2 and then Step 3 asynchronously', async () => {
    // Setup API mocks for the flow
    (inspectionsApi.createInspection as Mock).mockResolvedValue({ id: 'insp1' });
    (inspectionsApi.uploadInspectionImage as Mock).mockResolvedValue({ id: 'img1', object_key: 'obj1' });
    (inspectionsApi.analyzeImage as Mock).mockResolvedValue({ job_id: 'job1', status: 'QUEUED' });
    
    // First polling call returns PROCESSING, second returns COMPLETED
    (analysisApi.getAnalysisJob as Mock)
      .mockResolvedValueOnce({ job_id: 'job1', status: 'PROCESSING' })
      .mockResolvedValueOnce({ job_id: 'job1', status: 'COMPLETED' });

    renderComponent();
    
    // Wait for buildings to load
    await waitFor(() => {
      expect(screen.getByText('-- Select Building --')).toBeInTheDocument();
    });

    // Step 1: Select hierarchy
    fireEvent.change(screen.getByRole('combobox', { name: /building/i }), { target: { value: 'b1' } });
    
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: /floor/i })).toBeInTheDocument();
    });
    fireEvent.change(screen.getByRole('combobox', { name: /floor/i }), { target: { value: 'f1' } });
    
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: /area/i })).toBeInTheDocument();
    });
    fireEvent.change(screen.getByRole('combobox', { name: /area/i }), { target: { value: 'a1' } });
    
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: /structural element/i })).toBeInTheDocument();
    });
    fireEvent.change(screen.getByRole('combobox', { name: /structural element/i }), { target: { value: 'e1' } });

    // Click Continue
    const continueBtn = screen.getByRole('button', { name: /continue to image inspection/i });
    expect(continueBtn).not.toBeDisabled();
    fireEvent.click(continueBtn);

    // Step 2: Upload Image
    await waitFor(() => {
      expect(screen.getByText('2. Capture Defect')).toBeInTheDocument();
    });
    
    // Simulate file upload
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['dummy content'], 'test.png', { type: 'image/png' });
    Object.defineProperty(fileInput, 'files', {
      value: [file]
    });
    fireEvent.change(fileInput);

    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });

    // Click Analyze
    const analyzeBtn = screen.getByRole('button', { name: /analyze image/i });
    fireEvent.click(analyzeBtn);

    // Verify UI transitions to Step 3 and polls
    await waitFor(() => {
      expect(screen.getByText('Analysis Queued...')).toBeInTheDocument();
    });
    
    await waitFor(() => {
      expect(screen.getByText('Analysis In Progress...')).toBeInTheDocument();
    }, { timeout: 3000 });
    
    await waitFor(() => {
      expect(screen.getByText('Analysis Completed')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByText('Defect observation captured and analysis generated successfully.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /view engineering report/i })).toBeInTheDocument();
  });
  
  it('handles FAILED job state correctly', async () => {
    (inspectionsApi.createInspection as Mock).mockResolvedValue({ id: 'insp1' });
    (inspectionsApi.uploadInspectionImage as Mock).mockResolvedValue({ id: 'img1', object_key: 'obj1' });
    (inspectionsApi.analyzeImage as Mock).mockResolvedValue({ job_id: 'job1', status: 'QUEUED' });
    
    (analysisApi.getAnalysisJob as Mock).mockResolvedValue({ 
      job_id: 'job1', 
      status: 'FAILED',
      error_message: 'Model execution failed'
    });

    renderComponent();
    
    // Jump to step 1 filled
    await waitFor(() => screen.getByRole('combobox', { name: /building/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /building/i }), { target: { value: 'b1' } });
    await waitFor(() => screen.getByRole('combobox', { name: /floor/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /floor/i }), { target: { value: 'f1' } });
    await waitFor(() => screen.getByRole('combobox', { name: /area/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /area/i }), { target: { value: 'a1' } });
    await waitFor(() => screen.getByRole('combobox', { name: /structural element/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /structural element/i }), { target: { value: 'e1' } });
    fireEvent.click(screen.getByRole('button', { name: /continue to image inspection/i }));

    // Step 2 file
    await waitFor(() => screen.getByText('2. Capture Defect'));
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['dummy content'], 'test.png', { type: 'image/png' });
    Object.defineProperty(fileInput, 'files', { value: [file] });
    fireEvent.change(fileInput);
    
    // Step 3 trigger
    await waitFor(() => screen.getByRole('button', { name: /analyze image/i }));
    fireEvent.click(screen.getByRole('button', { name: /analyze image/i }));
    
    await waitFor(() => {
      expect(screen.getByText('Analysis Failed')).toBeInTheDocument();
      expect(screen.getByText('Model execution failed')).toBeInTheDocument();
    }, { timeout: 3000 });
    
    const tryAgainBtn = screen.getByRole('button', { name: /try again/i });
    expect(tryAgainBtn).toBeInTheDocument();
    fireEvent.click(tryAgainBtn);
    
    await waitFor(() => {
      expect(screen.getByText('2. Capture Defect')).toBeInTheDocument();
    });
  });
});
