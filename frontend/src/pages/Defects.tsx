import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '../components/ui';
import { getDefects, Defect } from '../api/defects';
import { AlertTriangle, Clock, CheckCircle, XCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Defects = () => {
  const navigate = useNavigate();
  const [defects, setDefects] = useState<Defect[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getDefects().then(setDefects).catch(console.error).finally(() => setIsLoading(false));
  }, []);

  const getStatusConfig = (status: string) => {
    switch(status) {
      case 'CANDIDATE': return { color: 'warning', icon: AlertTriangle, text: 'Candidate (Pending Review)' };
      case 'MONITORED': return { color: 'default', icon: Clock, text: 'Monitored' };
      case 'REPAIRED': return { color: 'success', icon: CheckCircle, text: 'Repaired' };
      case 'DISMISSED': return { color: 'default', icon: XCircle, text: 'Dismissed' };
      default: return { color: 'default', icon: AlertTriangle, text: status };
    }
  };

  if (isLoading) return <div className="p-8 text-slate-500 dark:text-slate-400">Loading defects...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Defect Register</h1>
        <p className="text-slate-500 dark:text-slate-400">View and manage structural defects across all your buildings.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Defects</CardTitle>
        </CardHeader>
        <CardContent>
          {defects.length === 0 ? (
            <div className="text-center py-8 text-slate-500 dark:text-slate-400 text-sm">
              No defects recorded yet. Start an inspection to capture defects.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-slate-500 dark:text-slate-400">
                <thead className="text-xs text-slate-700 dark:text-slate-300 uppercase bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Date Recorded</th>
                  </tr>
                </thead>
                <tbody>
                  {defects.map(defect => {
                    const cfg = getStatusConfig(defect.status);
                    const StatusIcon = cfg.icon;
                    return (
                      <tr key={defect.id} onClick={() => navigate(`/defects/${defect.id}`)} className="border-b border-slate-100 hover:bg-slate-50 dark:bg-slate-900/50 cursor-pointer">
                        <td className="px-4 py-3 font-medium text-slate-900 dark:text-white capitalize">
                          {defect.defect_type}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={cfg.color as any} className="flex w-fit items-center gap-1">
                            <StatusIcon className="h-3 w-3" />
                            {cfg.text}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          {new Date(defect.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
