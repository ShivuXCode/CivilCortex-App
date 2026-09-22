
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach, Mock } from 'vitest';
import { Report } from './Report';
import { getAssessment, getReport } from '../api/inspections';
import { updateAssessment } from '../api/defects';
import { renderWithProviders } from '../test/utils';
import { mockInspectorUser, mockEngineerUser, mockAssessment, mockReport } from '../test/fixtures';

vi.mock('../api/inspections', () => ({
  getAssessment: vi.fn(),
  getReport: vi.fn(),
}));

vi.mock('../api/defects', () => ({
  updateAssessment: vi.fn(),
}));

const renderReportPage = (user: any) => {
  return renderWithProviders(
    <Routes>
      <Route path="/inspections/:id/report" element={<Report />} />
    </Routes>,
    { route: '/inspections/123/report', user }
  );
};

describe('Report component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    (getAssessment as Mock).mockImplementation(() => new Promise(() => {}));
    (getReport as Mock).mockImplementation(() => new Promise(() => {}));

    renderReportPage(mockInspectorUser);
    expect(screen.getByText('Loading assessment...')).toBeInTheDocument();
  });

  it('renders NOT_FOUND / error state when no assessment exists', async () => {
    (getAssessment as Mock).mockResolvedValue([]);
    (getReport as Mock).mockResolvedValue(null);

    renderReportPage(mockInspectorUser);

    await waitFor(() => {
      expect(screen.getByText('No assessment has been generated for this inspection yet.')).toBeInTheDocument();
    });
  });

  it('renders assessment and report data successfully', async () => {
    (getAssessment as Mock).mockResolvedValue([mockAssessment]);
    (getReport as Mock).mockResolvedValue(mockReport);

    renderReportPage(mockInspectorUser);

    // Wait for the UI to load
    await waitFor(() => {
      expect(screen.getByText('Engineering Assessment Report')).toBeInTheDocument();
    });

    // Check Risk Assessment section
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('REQUIRES ENGINEER REVIEW')).toBeInTheDocument(); // matches mock fixture
    expect(screen.getAllByText('Immediate shoring recommended')[0]).toBeInTheDocument();

    // Check RAG section fallback
    expect(screen.getByText('No relevant regulatory evidence was retrieved.')).toBeInTheDocument();

    // Check Executive Report section (react-markdown rendering)
    expect(screen.getAllByText('Executive Report')[0]).toBeInTheDocument();
    expect(screen.getByText('Findings')).toBeInTheDocument();
    expect(screen.getByText('Severe cracking found in main pillar.')).toBeInTheDocument();
  });

  it('hides engineer review controls from inspectors', async () => {
    (getAssessment as Mock).mockResolvedValue([mockAssessment]);
    (getReport as Mock).mockResolvedValue(mockReport);

    renderReportPage(mockInspectorUser);

    await waitFor(() => {
      expect(screen.getByText('Engineering Assessment Report')).toBeInTheDocument();
    });

    // Inspector should not see the update controls
    expect(screen.queryByRole('button', { name: /save assessment review/i })).not.toBeInTheDocument();
    expect(screen.queryByText('Engineer Review')).not.toBeInTheDocument();
  });

  it('sanitizes malicious markdown content (XSS protection)', async () => {
    (getAssessment as Mock).mockResolvedValue([mockAssessment]);
    
    // Malicious report content
    const maliciousReport = {
      status: 'COMPLETED',
      content: '# Alert\n<script>alert("XSS")</script>\n[Click me](javascript:alert("XSS"))\n<a href="javascript:alert(1)">Evil</a>',
      generated_at: '2023-10-01T00:00:00Z'
    };
    (getReport as Mock).mockResolvedValue(maliciousReport);

    renderReportPage(mockInspectorUser);

    await waitFor(() => {
      expect(screen.getByText('Engineering Assessment Report')).toBeInTheDocument();
    });

    // Text renders
    expect(screen.getByText('Alert')).toBeInTheDocument();
    
    // Script tag is neutralized by react-markdown default sanitization
    // A javascript link should be neutralized
    const link = screen.getByText('Click me');
    expect(link).toHaveAttribute('href', ''); // react-markdown strips javascript protocols
    
    // The script alert shouldn't be rendered as an active script
    expect(document.querySelector('script')).not.toBeInTheDocument();
  });

  it('allows engineer to update assessment', async () => {
    (getAssessment as Mock).mockResolvedValue([mockAssessment]);
    (getReport as Mock).mockResolvedValue(mockReport);
    
    (updateAssessment as Mock).mockResolvedValue({
      ...mockAssessment,
      severity: 'CRITICAL',
      risk: 'REQUIRES_ENGINEER_REVIEW',
      repair_recommendation: 'Patch and monitor'
    });

    renderReportPage(mockEngineerUser);

    await waitFor(() => {
      expect(screen.getByText('Engineer Review')).toBeInTheDocument();
    });

    // Change severity
    const severitySelect = screen.getByLabelText('Override Severity');
    fireEvent.change(severitySelect, { target: { value: 'CRITICAL' } });

    // Change risk
    const riskSelect = screen.getByLabelText('Override Risk');
    fireEvent.change(riskSelect, { target: { value: 'REQUIRES_ENGINEER_REVIEW' } });

    // Change recommendation
    const textarea = screen.getByLabelText('Engineering Recommendation / Action Plan');
    fireEvent.change(textarea, { target: { value: 'Patch and monitor' } });

    // Submit
    const saveButton = screen.getByRole('button', { name: /save assessment review/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(updateAssessment).toHaveBeenCalledWith(mockAssessment.id, {
        severity: 'CRITICAL',
        risk: 'REQUIRES_ENGINEER_REVIEW',
        repair_recommendation: 'Patch and monitor'
      });
      expect(screen.getByText('Assessment updated successfully.')).toBeInTheDocument();
    });
  });
});
