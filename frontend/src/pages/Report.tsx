import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getAssessment, getReport, AssessmentResponse, ReportResponse, downloadReportPDF, downloadReportDOCX } from '../api/inspections';
import { updateAssessment } from '../api/defects';
import { ShieldAlert, FileText, Activity, AlertTriangle, ArrowLeft, Clock } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { AuditHistoryModal } from '../components/AuditHistoryModal';

const RAGEvidenceFormatter = ({ evidenceText }: { evidenceText: string }) => {
  if (!evidenceText) return null;
  const sources = evidenceText.split('Source: ').filter(Boolean);
  
  return (
    <div className="space-y-6">
      {sources.map((sourceBlock, idx) => {
        const firstNewlineIndex = sourceBlock.indexOf('\n');
        let sourceName = sourceBlock.trim();
        let content = '';

        if (firstNewlineIndex !== -1) {
          sourceName = sourceBlock.substring(0, firstNewlineIndex).trim();
          content = sourceBlock.substring(firstNewlineIndex + 1).trim();
        }

        const regex = /(MBI\s+Figure\s+[\d.]+|Figure\s+[\d.]+|Chapter\s+\d+|Section\s+[\d.]+|Page\s+\d+|•)/gi;
        const tokens = content.split(regex);
        
        const elements: { id: number; type: string; text: string }[] = [];
        
        tokens.forEach((t) => {
          if (!t) return;
          const isBullet = t === '•';
          const isFigure = /^(MBI\s+)?Figure\s+[\d.]+/i.test(t);
          const isMeta = /^(Chapter\s+\d+|Section\s+[\d.]+|Page\s+\d+)/i.test(t);
          
          if (isBullet) {
            elements.push({ id: elements.length, type: 'bullet', text: '' });
          } else if (isFigure) {
            elements.push({ id: elements.length, type: 'figure', text: t.trim() });
          } else if (isMeta) {
            elements.push({ id: elements.length, type: 'meta', text: t.trim() });
          } else {
            const text = t.trim();
            if (!text) return;
            
            const last = elements[elements.length - 1];
            if (last && last.type === 'bullet' && !last.text) {
              last.text = text;
            } else {
              elements.push({ id: elements.length, type: 'text', text });
            }
          }
        });

        return (
          <div key={idx} className="evidence-container bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
            <div className="bg-slate-50 dark:bg-slate-800 px-4 py-3 border-b border-slate-200 dark:border-slate-700">
              <h4 className="font-medium text-slate-800 dark:text-slate-200 flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4 text-slate-500" />
                Source: <span className="font-mono text-xs bg-slate-200 dark:bg-slate-700 px-2 py-1 rounded text-slate-700 dark:text-slate-300">{sourceName}</span>
              </h4>
            </div>
            
            <div className="p-4 space-y-3">
              {elements.map((el) => {
                if (el.type === 'bullet') {
                  return (
                    <ul key={el.id} className="evidence-list list-disc list-outside ml-5 text-sm text-slate-700 dark:text-slate-300">
                      <li className="evidence-item">{el.text}</li>
                    </ul>
                  );
                }
                
                if (el.type === 'meta') {
                  return (
                    <div key={el.id} className="metadata-section text-xs font-semibold tracking-wide text-indigo-600 dark:text-indigo-400 uppercase mb-1">
                      {el.text}
                    </div>
                  );
                }
                
                if (el.type === 'figure') {
                  return (
                    <div key={el.id} className="italic text-sm text-slate-500 dark:text-slate-400 my-2 bg-slate-50 dark:bg-slate-800/50 px-3 py-2 rounded border border-slate-100 dark:border-slate-700 inline-block">
                      {el.text}
                    </div>
                  );
                }
                
                return <p key={el.id} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{el.text}</p>;
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export const Report = () => {
  const { user } = useAuth();
  const { id: inspectionId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);

  const [editSeverity, setEditSeverity] = useState('');
  const [editRisk, setEditRisk] = useState('');
  const [editRecommendation, setEditRecommendation] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateMessage, setUpdateMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [showAuditModal, setShowAuditModal] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (!inspectionId) return;
      setIsLoading(true);
      setError(null);
      try {
        const [assessmentsData, reportData] = await Promise.all([
          getAssessment(inspectionId).catch(() => []),
          getReport(inspectionId).catch(() => null)
        ]);

        if (assessmentsData && assessmentsData.length > 0) {
          const currentAssessment = assessmentsData[0];
          setAssessment(currentAssessment);
          setEditSeverity('UNKNOWN');
          setEditRisk('UNKNOWN');
          setEditRecommendation('');
        } else {
          setError('No assessment has been generated for this inspection yet.');
        }

        if (reportData) {
          setReport(reportData);
        }

      } catch (err) {
        setError('Unable to load the assessment. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [inspectionId]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assessment) return;
    
    setIsUpdating(true);
    setUpdateMessage(null);
    try {
      const updated = await updateAssessment(assessment.id, {
        severity: editSeverity,
        risk: editRisk,
        repair_recommendation: editRecommendation
      });
      
      setAssessment(updated);
      setUpdateMessage({ type: 'success', text: 'Assessment updated successfully.' });
    } catch (err) {
      setUpdateMessage({ type: 'error', text: 'Failed to update assessment.' });
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-500 dark:text-slate-400">
        <Activity className="h-6 w-6 animate-pulse mr-2" />
        Loading assessment...
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Button variant="ghost" onClick={() => navigate('/defects')} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Dashboard
        </Button>
        <Card className="border-red-200">
          <CardContent className="p-8 text-center text-red-600">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4" />
            <p className="font-medium text-lg">{error || 'Assessment not found'}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div>
        <Button variant="ghost" onClick={() => navigate('/defects')} className="mb-4 -ml-4">
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Defects
        </Button>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Engineering Assessment Report</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">AI-assisted structural defect analysis and risk evaluation</p>
      </div>

      <Card>
        <CardHeader className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-100">
          <CardTitle className="text-lg flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-slate-500 dark:text-slate-400" />
            Risk Assessment
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-1">
              <span className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Severity</span>
              <p className="text-2xl font-semibold capitalize text-slate-900 dark:text-white">{assessment.severity}</p>
            </div>
            <div className="space-y-1 flex justify-between items-start">
              <div>
                <span className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Risk Level</span>
                <p className="text-2xl font-semibold capitalize text-slate-900 dark:text-white">{assessment.risk.replace(/_/g, ' ')}</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setShowAuditModal(true)} className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                View History
              </Button>
            </div>
            <div className="col-span-2 space-y-1 mt-4">
              <span className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-2">AI-Generated Recommendation</span>
              <div className="bg-amber-50 border border-amber-200 rounded-md p-4 text-amber-900 text-sm leading-relaxed">
                {assessment.repair_recommendation || "No specific recommendation was generated."}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {showAuditModal && (
        <AuditHistoryModal 
          assessmentId={assessment.id} 
          onClose={() => setShowAuditModal(false)} 
        />
      )}

      <Card>
        <CardHeader className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-100">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileText className="h-5 w-5 text-slate-500 dark:text-slate-400" />
            Regulatory / RAG Evidence
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          {assessment.rag_context ? (
            <RAGEvidenceFormatter evidenceText={assessment.rag_context} />
          ) : (
            <p className="text-slate-600 dark:text-slate-400 italic">No relevant regulatory evidence was retrieved.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="bg-slate-50 dark:bg-slate-900/50 border-b border-slate-100">
          <div className="flex justify-between items-center w-full">
            <CardTitle className="text-lg">Executive Report</CardTitle>
            <div className="relative group">
              <Button variant="outline" size="sm" className="flex items-center gap-2">
                Download Report
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
              </Button>
              <div className="absolute right-0 pt-2 w-48 hidden group-hover:block group-focus-within:block z-50">
                <div className="bg-white dark:bg-slate-800 rounded-md shadow-lg border border-slate-200 dark:border-slate-700 py-1">
                  <button
                    className="block w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                    onClick={async () => {
                      try {
                        const blob = await downloadReportPDF(inspectionId!);
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `CivilCortex_Report_${inspectionId}.pdf`;
                        a.click();
                        window.URL.revokeObjectURL(url);
                      } catch (e) {
                        console.error("PDF Download failed", e);
                      }
                    }}
                  >
                    Download as PDF
                  </button>
                  <button
                    className="block w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                    onClick={async () => {
                      try {
                        const blob = await downloadReportDOCX(inspectionId!);
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `CivilCortex_Report_${inspectionId}.docx`;
                        a.click();
                        window.URL.revokeObjectURL(url);
                      } catch (e) {
                        console.error("DOCX Download failed", e);
                      }
                    }}
                  >
                    Download as Word (.docx)
                  </button>
                </div>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          {report ? (
            <div className="prose prose-slate max-w-none text-sm">
              <ReactMarkdown>{report.content}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-slate-500 dark:text-slate-400 italic">Executive report generation is still pending or unavailable.</p>
          )}
        </CardContent>
      </Card>

      {user?.role !== 'INSPECTOR' && (
        <Card className="border-indigo-100 shadow-sm">
          <CardHeader className="bg-indigo-50/50 border-b border-indigo-100">
          <CardTitle className="text-lg text-indigo-900">Engineer Review</CardTitle>
          <p className="text-sm text-indigo-700/70">Modify the assessment based on engineering judgment.</p>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleUpdate} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="severity-select" className="text-sm font-medium text-slate-700 dark:text-slate-300">Override Severity</label>
                <select 
                  id="severity-select"
                  className="block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm border bg-white dark:bg-slate-800"
                  value={editSeverity}
                  onChange={e => setEditSeverity(e.target.value)}
                >
                  <option value="UNKNOWN">Unknown</option>
                  <option value="LOW">Low</option>
                  <option value="MODERATE">Moderate</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div className="space-y-2">
                <label htmlFor="risk-select" className="text-sm font-medium text-slate-700 dark:text-slate-300">Override Risk</label>
                <select 
                  id="risk-select"
                  className="block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm border bg-white dark:bg-slate-800"
                  value={editRisk}
                  onChange={e => setEditRisk(e.target.value)}
                >
                  <option value="UNKNOWN">Unknown</option>
                  <option value="LOW">Low</option>
                  <option value="MODERATE">Moderate</option>
                  <option value="HIGH">High</option>
                  <option value="REQUIRES_REVIEW">Requires Review</option>
                  <option value="REQUIRES_ENGINEER_REVIEW">Requires Engineer Review</option>
                </select>
              </div>
            </div>
            
            <div className="space-y-2">
              <label htmlFor="recommendation-textarea" className="text-sm font-medium text-slate-700 dark:text-slate-300">Engineering Recommendation / Action Plan</label>
              <textarea 
                id="recommendation-textarea"
                className="block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 px-3 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm border bg-white dark:bg-slate-800"
                rows={4}
                value={editRecommendation}
                onChange={e => setEditRecommendation(e.target.value)}
              />
            </div>

            {updateMessage && (
              <div className={`p-3 rounded-md text-sm font-medium ${updateMessage.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'}`}>
                {updateMessage.text}
              </div>
            )}

            <div className="flex justify-end pt-2">
              <Button type="submit" disabled={isUpdating} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                {isUpdating ? 'Saving...' : 'Save Assessment Review'}
              </Button>
            </div>
          </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
