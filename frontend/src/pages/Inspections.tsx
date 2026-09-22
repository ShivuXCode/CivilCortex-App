import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge } from '../components/ui';
import { getInspections, Inspection } from '../api/inspections';
import { useNavigate } from 'react-router-dom';
import { ClipboardCheck, ArrowRight, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

export const Inspections = () => {
  const navigate = useNavigate();
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getInspections().then(setInspections).catch(console.error).finally(() => setIsLoading(false));
  }, []);

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'DRAFT': return <Badge variant="default" className="bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200 border-slate-200 dark:border-slate-700">Draft</Badge>;
      case 'SUBMITTED': return <Badge variant="warning" className="flex items-center gap-1"><Clock className="w-3 h-3"/> Submitted</Badge>;
      case 'AI_ANALYSIS': return <Badge variant="warning" className="flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> AI Analysis</Badge>;
      case 'ASSESSMENT_READY': return <Badge variant="success" className="flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Assessment Ready</Badge>;
      case 'UNDER_ENGINEER_REVIEW': return <Badge variant="warning" className="flex items-center gap-1"><Clock className="w-3 h-3"/> Under Review</Badge>;
      case 'REVISION_REQUIRED': return <Badge variant="destructive" className="flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Revision Required</Badge>;
      case 'APPROVED': return <Badge variant="success" className="flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Approved</Badge>;
      case 'REPORT_GENERATED': return <Badge variant="success" className="flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Report Ready</Badge>;
      case 'COMPLETED': return <Badge variant="success" className="flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Completed</Badge>;
      default: return <Badge variant="default">{status}</Badge>;
    }
  };

  if (isLoading) return <div className="p-8 text-slate-500 dark:text-slate-400">Loading inspections...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Inspections</h1>
          <p className="text-slate-500 dark:text-slate-400">Manage all structural inspections across your buildings.</p>
        </div>
        <Button onClick={() => navigate('/inspections/new')}>Start New Inspection</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Organization Inspections</CardTitle>
        </CardHeader>
        <CardContent>
          {inspections.length === 0 ? (
            <div className="text-center py-8 text-slate-500 dark:text-slate-400 text-sm">
              No inspections found. Start a new inspection to begin.
            </div>
          ) : (
            <div className="space-y-4">
              {inspections.map(insp => (
                <div key={insp.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 hover:bg-slate-100 dark:bg-slate-900 transition-colors">
                  <div className="flex items-center gap-4 mb-4 sm:mb-0">
                    <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                      <ClipboardCheck className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 dark:text-white">Inspection {insp.id.substring(0, 8)}</div>
                      <div className="text-sm text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
                        Status: {getStatusBadge(insp.status)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {insp.status === 'REPORT_GENERATED' || insp.status === 'COMPLETED' ? (
                      <Button variant="outline" size="sm" onClick={() => navigate(`/inspections/${insp.id}/report`)}>
                        View Report
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" onClick={() => navigate(`/inspections/${insp.id}/report`)}>
                        View Status <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
