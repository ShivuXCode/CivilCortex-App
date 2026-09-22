import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Badge, Button } from '../components/ui';
import { getDefect, Defect } from '../api/defects';
import { ArrowLeft, AlertTriangle, Clock, CheckCircle, XCircle } from 'lucide-react';

export const DefectDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [defect, setDefect] = useState<Defect | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getDefect(id)
        .then(setDefect)
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [id]);

  const getStatusConfig = (status: string) => {
    switch(status) {
      case 'CANDIDATE': return { color: 'warning', icon: AlertTriangle, text: 'Candidate (Pending Review)' };
      case 'MONITORED': return { color: 'default', icon: Clock, text: 'Monitored' };
      case 'REPAIRED': return { color: 'success', icon: CheckCircle, text: 'Repaired' };
      case 'DISMISSED': return { color: 'default', icon: XCircle, text: 'Dismissed' };
      default: return { color: 'default', icon: AlertTriangle, text: status };
    }
  };

  if (isLoading) return <div className="p-8 text-slate-500 dark:text-slate-400">Loading defect details...</div>;
  if (!defect) return <div className="p-8 text-slate-500 dark:text-slate-400">Defect not found.</div>;

  const cfg = getStatusConfig(defect.status);
  const StatusIcon = cfg.icon;

  return (
    <div className="space-y-6 max-w-4xl">
      <Button variant="ghost" onClick={() => navigate('/defects')} className="mb-4">
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to Defects
      </Button>

      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white capitalize">
          {defect.defect_type} Defect Details
        </h1>
        <p className="text-slate-500 dark:text-slate-400">ID: {defect.id}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Defect Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">Status</div>
              <Badge variant={cfg.color as any} className="flex w-fit items-center gap-1">
                <StatusIcon className="h-3 w-3" />
                {cfg.text}
              </Badge>
            </div>
            
            <div>
              <div className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">Type</div>
              <div className="font-medium text-slate-900 dark:text-white capitalize">{defect.defect_type}</div>
            </div>

            <div>
              <div className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">Structural Element ID</div>
              <div className="font-medium text-slate-900 dark:text-white">{defect.structural_element_id || 'N/A (AI Generated / Unassigned)'}</div>
            </div>

            <div>
              <div className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">Date Recorded</div>
              <div className="font-medium text-slate-900 dark:text-white">{new Date(defect.created_at).toLocaleDateString()}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
