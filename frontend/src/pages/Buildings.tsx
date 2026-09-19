import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '../components/ui';
import { getBuildings, createBuilding, createFloor, createArea, createStructuralElement, Building } from '../api/hierarchy';
import { Search, Plus, Building2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Buildings = () => {
  const navigate = useNavigate();
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [newBuildingName, setNewBuildingName] = useState('');
  const [newBuildingLocation, setNewBuildingLocation] = useState('');
  const [numFloors, setNumFloors] = useState(1);
  const [isSaving, setIsSaving] = useState(false);

  const fetchBuildings = async () => {
    try {
      const data = await getBuildings();
      setBuildings(data);
    } catch (err) {
      console.error("Failed to fetch buildings");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBuildings();
  }, []);

  const handleAddBuilding = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBuildingName.trim()) return;

    setIsSaving(true);
    try {
      // 1. Create the building
      const building = await createBuilding({
        name: newBuildingName,
        location: newBuildingLocation || undefined,
      });

      // 2. Auto-create floors, areas, and structural elements (full hierarchy)
      const floorCount = Math.max(1, Math.min(numFloors, 50));
      const defaultAreas = ['Columns', 'Beams', 'Walls', 'Ceiling', 'Foundation'];
      const defaultElements: { name: string; element_type: string }[] = [
        { name: 'Column C1', element_type: 'Column' },
        { name: 'Column C2', element_type: 'Column' },
        { name: 'Beam B1',   element_type: 'Beam' },
        { name: 'Wall W1',   element_type: 'Wall' },
        { name: 'Slab S1',   element_type: 'Slab' },
      ];
      for (let i = 1; i <= floorCount; i++) {
        const floor = await createFloor({ name: `Floor ${i}`, level: i, building_id: building.id });
        for (const areaName of defaultAreas) {
          const area = await createArea({ name: areaName, floor_id: floor.id });
          for (const el of defaultElements) {
            await createStructuralElement({ name: el.name, element_type: el.element_type, area_id: area.id });
          }
        }
      }

      setNewBuildingName('');
      setNewBuildingLocation('');
      setNumFloors(1);
      setIsAdding(false);
      fetchBuildings();
    } catch (err) {
      console.error("Failed to create building");
    } finally {
      setIsSaving(false);
    }
  };

  const filteredBuildings = buildings.filter(b =>
    b.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Buildings</h1>
          <p className="text-slate-500">Manage your inspection sites and structures.</p>
        </div>
        <Button onClick={() => setIsAdding(!isAdding)}>
          <Plus className="mr-2 h-4 w-4" /> Add Building
        </Button>
      </div>

      {isAdding && (
        <Card className="bg-slate-50 border-dashed">
          <CardContent className="pt-6">
            <form onSubmit={handleAddBuilding} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="sm:col-span-1 space-y-2">
                  <label className="text-sm font-medium text-slate-700">Building Name *</label>
                  <Input
                    value={newBuildingName}
                    onChange={(e) => setNewBuildingName(e.target.value)}
                    placeholder="e.g., North Wing"
                    autoFocus
                    required
                  />
                </div>
                <div className="sm:col-span-1 space-y-2">
                  <label className="text-sm font-medium text-slate-700">Location</label>
                  <Input
                    value={newBuildingLocation}
                    onChange={(e) => setNewBuildingLocation(e.target.value)}
                    placeholder="e.g., Site A, Block 3"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Number of Floors *</label>
                  <Input
                    type="number"
                    min={1}
                    max={50}
                    value={numFloors}
                    onChange={(e) => setNumFloors(parseInt(e.target.value) || 1)}
                    placeholder="e.g., 5"
                    required
                  />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Button type="submit" disabled={isSaving}>
                  {isSaving ? 'Creating...' : 'Save Building'}
                </Button>
                <Button variant="ghost" type="button" onClick={() => setIsAdding(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <Input
          className="pl-9"
          placeholder="Search buildings..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="text-slate-500 text-center py-12">Loading buildings...</div>
      ) : filteredBuildings.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-slate-100 p-3 mb-4">
              <Building2 className="h-6 w-6 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">No buildings found</h3>
            <p className="text-sm text-slate-500 max-w-sm mt-1">
              Get started by adding a building to track structural elements and inspections.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredBuildings.map((building) => (
            <Card key={building.id} className="cursor-pointer hover:border-slate-300 transition-colors" onClick={() => navigate(`/buildings/${building.id}`)}>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">{building.name}</CardTitle>
                {building.location && <p className="text-sm text-slate-500">{building.location}</p>}
              </CardHeader>
              <CardContent>
                <div className="text-sm text-slate-500 flex items-center justify-between">
                  <span>Added {new Date(building.created_at).toLocaleDateString()}</span>
                  <span className="font-medium text-slate-900 hover:underline">View details &rarr;</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
