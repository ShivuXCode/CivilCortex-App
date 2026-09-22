import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getBuildings } from '../api/hierarchy';
import { getInspections, Inspection, submitInspection, beginReview, approveInspection, generateReport } from '../api/inspections';
import { getDefects } from '../api/defects';
import { useAuth } from '../hooks/useAuth';

export const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    buildings: 0,
    activeInspections: 0,
    openDefects: 0,
  });
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [buildings, allInspections, defects] = await Promise.all([
          getBuildings(),
          getInspections(),
          getDefects()
        ]);
        
        const openDefectsCount = defects.filter(d => 
          d.status === 'CANDIDATE' || d.status === 'MONITORED'
        ).length;
        
        setStats({
          buildings: buildings.length,
          activeInspections: allInspections.length,
          openDefects: openDefectsCount
        });

        setInspections(allInspections);
      } catch (err) {
        console.error("Failed to load dashboard data");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [user]);

  const handleAction = async (action: () => Promise<any>) => {
    try {
      await action();
      const updated = await getInspections();
      setInspections(updated);
    } catch (err) {
      alert("Action failed");
    }
  };

  const getActionForStatus = (insp: Inspection) => {
    switch (insp.status) {
      case 'DRAFT':
        return <Button size="sm" onClick={() => handleAction(() => submitInspection(insp.id))}>Submit to AI</Button>;
      case 'ASSESSMENT_READY':
        return <Button size="sm" onClick={() => handleAction(() => beginReview(insp.id))}>Begin Review</Button>;
      case 'UNDER_ENGINEER_REVIEW':
        return (
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => navigate(`/inspections/${insp.id}/report`)}>View Data</Button>
            <Button size="sm" onClick={() => handleAction(() => approveInspection(insp.id))}>Approve</Button>
          </div>
        );
      case 'APPROVED':
        return <Button size="sm" onClick={() => handleAction(() => generateReport(insp.id))}>Generate Report</Button>;
      case 'REPORT_GENERATED':
      case 'COMPLETED':
        return <Button size="sm" variant="outline" onClick={() => navigate(`/inspections/${insp.id}/report`)}>View Report</Button>;
      default:
        return <span className="text-sm text-slate-500">Processing...</span>;
    }
  };

  if (isLoading) return <div className="p-8 text-slate-500">Loading unified dashboard...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
        <Button onClick={() => navigate('/inspections/new')}>Start New Inspection</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase">Total Buildings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{stats.buildings}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase">Active Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{stats.activeInspections}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase">Open Defects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-900">{stats.openDefects}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Organization Inspections</CardTitle>
        </CardHeader>
        <CardContent>
          {inspections.length === 0 ? (
            <p className="text-slate-500">No inspections found.</p>
          ) : (
            <div className="space-y-4">
              {inspections.map(insp => (
                <div key={insp.id} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 border rounded-lg bg-white shadow-sm gap-4">
                  <div>
                    <h3 className="font-semibold text-slate-900">Inspection {insp.id.substring(0,8)}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-slate-500">Status:</span>
                      <span className="text-xs font-medium px-2 py-1 bg-slate-100 rounded-full">{insp.status}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {getActionForStatus(insp)}
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
