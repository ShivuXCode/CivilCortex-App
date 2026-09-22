import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Badge } from '../components/ui';
import { getInspections, Inspection } from '../api/inspections';
import { useNavigate } from 'react-router-dom';
import { FileText, ArrowRight, CheckCircle } from 'lucide-react';

export const Reports = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getInspections()
      .then(data => {
        // Only show inspections that have successfully generated reports
        const completedReports = data.filter(insp => 
          insp.status === 'REPORT_GENERATED' || insp.status === 'COMPLETED'
        );
        setReports(completedReports);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div className="p-8 text-slate-500 dark:text-slate-400">Loading reports...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Engineering Reports</h1>
        <p className="text-slate-500 dark:text-slate-400">Access final structural engineering reports for completed inspections.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Available Reports</CardTitle>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <div className="text-center py-8 text-slate-500 dark:text-slate-400 text-sm">
              No reports available yet. Complete an inspection workflow to generate a report.
            </div>
          ) : (
            <div className="space-y-4">
              {reports.map(insp => (
                <div key={insp.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 hover:bg-slate-100 dark:bg-slate-900 transition-colors">
                  <div className="flex items-center gap-4 mb-4 sm:mb-0">
                    <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 dark:text-white">Executive Report - Inspection {insp.id.substring(0, 8)}</div>
                      <div className="text-sm text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
                        Status: <Badge variant="success" className="flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Ready</Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => navigate(`/inspections/${insp.id}/report`)}>
                      View Full Report <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
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
