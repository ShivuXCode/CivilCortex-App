import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getBuildings } from '../api/hierarchy';
import { getInspections, Inspection, submitInspection } from '../api/inspections';
import { getDefects } from '../api/defects';
import { useAuth } from '../hooks/useAuth';

export const InspectorDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    buildings: 0,
    activeInspections: 0,
    openDefects: 0,
  });
  const [myInspections, setMyInspections] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [buildings, inspections, defects] = await Promise.all([
          getBuildings(),
          getInspections(),
          getDefects()
        ]);
        
        const openDefectsCount = defects.filter(d => 
          d.status === 'CANDIDATE' || d.status === 'MONITORED'
        ).length;
        
        setStats({
          buildings: buildings.length,
          activeInspections: inspections.length,
          openDefects: openDefectsCount
        });

        setMyInspections(inspections.filter(i => i.inspector_id === user?.id));
      } catch (err) {
        console.error("Failed to load dashboard data");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [user]);

  const handleSubmit = async (id: string) => {
    try {
      await submitInspection(id);
      const updated = await getInspections();
      setMyInspections(updated.filter(i => i.inspector_id === user?.id));
    } catch (err) {
      alert("Failed to submit inspection");
    }
  };

  if (isLoading) {
    return <div className="p-8 text-slate-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Inspector Dashboard</h1>
        <Button onClick={() => navigate('/inspections/new')}>
          + New Inspection
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Buildings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.buildings}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeInspections}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Defects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.openDefects}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>My Recent Inspections</CardTitle>
        </CardHeader>
        <CardContent>
          {myInspections.length === 0 ? (
             <p className="text-slate-500 py-4 text-center">No recent inspections found.</p>
          ) : (
            <div className="space-y-4">
              {myInspections.map(insp => (
                <div key={insp.id} className="p-4 border rounded flex justify-between items-center">
                  <div>
                    <div className="font-medium">Inspection {insp.id.substring(0,8)}</div>
                    <div className="text-sm text-slate-500">Status: {insp.status}</div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => navigate(`/inspections/${insp.id}/report`)}>
                      Details / Report
                    </Button>
                    {(insp.status === 'ASSESSMENT_READY' || insp.status === 'DRAFT' || insp.status === 'REVISION_REQUIRED' || insp.status === 'AI_ANALYSIS') && (
                      <Button onClick={() => handleSubmit(insp.id)}>
                        Submit to Review
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
