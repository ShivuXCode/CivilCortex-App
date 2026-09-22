import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getInspections, Inspection, beginReview, approveInspection, generateReport } from '../api/inspections';
import { useAuth } from '../hooks/useAuth';

export const EngineerDashboard = () => {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getInspections();
        setInspections(res.filter(i => i.assigned_engineer_id === user?.id));
      } catch (err) {
        console.error("Failed to load engineer data");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const handleAction = async (action: () => Promise<any>) => {
    try {
      await action();
      const updated = await getInspections();
      setInspections(updated.filter(i => i.assigned_engineer_id === user?.id));
    } catch (err) {
      alert("Action failed");
    }
  };

  if (isLoading) return <div className="p-8">Loading engineer dashboard...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Engineer Dashboard</h1>
      
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>My Assigned Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            {inspections.length === 0 ? (
              <p className="text-slate-500">No inspections assigned to you.</p>
            ) : (
              <div className="space-y-4">
                {inspections.map(insp => (
                  <div key={insp.id} className="p-4 border rounded flex justify-between items-center">
                    <div>
                      <div className="font-medium">Inspection {insp.id.substring(0,8)}</div>
                      <div className="text-sm text-slate-500">Status: {insp.status}</div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={() => navigate(`/inspections/${insp.id}/report`)}>
                        View Details
                      </Button>
                      
                      {insp.status === 'SUBMITTED' && (
                        <Button onClick={() => handleAction(() => beginReview(insp.id))}>Begin Review</Button>
                      )}
                      {insp.status === 'UNDER_ENGINEER_REVIEW' && (
                        <Button onClick={() => handleAction(() => approveInspection(insp.id))}>Approve</Button>
                      )}
                      {insp.status === 'APPROVED' && (
                        <Button onClick={() => handleAction(() => generateReport(insp.id))}>Generate Final Report</Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
