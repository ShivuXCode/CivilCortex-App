import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getBuilding, BuildingDetail as IBuildingDetail } from '../api/hierarchy';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const BuildingDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [building, setBuilding] = useState<IBuildingDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchBuilding = async () => {
      try {
        const data = await getBuilding(id);
        setBuilding(data);
      } catch (err) {
        console.error("Failed to load building details");
      } finally {
        setIsLoading(false);
      }
    };
    fetchBuilding();
  }, [id]);

  if (isLoading) return <div className="p-8 text-slate-500">Loading building details...</div>;
  if (!building) return <div className="p-8 text-red-500">Building not found or access denied.</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/buildings')} className="px-2">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{building.name}</h1>
          {building.location && <p className="text-slate-500">{building.location}</p>}
        </div>
      </div>

      <div className="flex justify-end gap-3">
        <Button onClick={() => navigate('/inspections/new')}>Start Inspection</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Structural Hierarchy</CardTitle>
        </CardHeader>
        <CardContent>
          {building.floors.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm border-2 border-dashed rounded-lg">
              No floors added yet. You will be able to add the hierarchy during your first inspection.
            </div>
          ) : (
            <div className="space-y-4">
              {building.floors.map(floor => (
                <div key={floor.id} className="pl-4 border-l-2 border-slate-200">
                  <h4 className="font-semibold text-slate-900">{floor.name}</h4>
                  
                  <div className="mt-2 space-y-3">
                    {floor.areas.map(area => (
                      <div key={area.id} className="pl-4 border-l-2 border-slate-100">
                        <h5 className="text-sm font-medium text-slate-700">{area.name}</h5>
                        
                        <div className="mt-1 flex flex-wrap gap-2">
                          {area.structural_elements.map(el => (
                            <span key={el.id} className="inline-flex items-center rounded-md bg-slate-50 px-2 py-1 text-xs font-medium text-slate-600 ring-1 ring-inset ring-slate-500/10">
                              {el.name} ({el.element_type})
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
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
