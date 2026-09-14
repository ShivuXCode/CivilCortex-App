import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getBuildings, getBuilding, Building, BuildingDetail } from '../api/hierarchy';
import { createInspection, uploadInspectionImage, analyzeImage, AnalysisResult } from '../api/inspections';
import { createDefect, createObservation } from '../api/defects';
import { UploadCloud, CheckCircle, AlertTriangle } from 'lucide-react';

export const NewInspection = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [buildingDetail, setBuildingDetail] = useState<BuildingDetail | null>(null);
  
  // Selection State
  const [selectedBuildingId, setSelectedBuildingId] = useState('');
  const [selectedFloorId, setSelectedFloorId] = useState('');
  const [selectedAreaId, setSelectedAreaId] = useState('');
  const [selectedElementId, setSelectedElementId] = useState('');

  // Workflow State
  const [inspectionId, setInspectionId] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [imageId, setImageId] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    getBuildings().then(setBuildings).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedBuildingId) {
      getBuilding(selectedBuildingId).then(setBuildingDetail).catch(console.error);
    }
  }, [selectedBuildingId]);

  const handleStartInspection = async () => {
    if (!selectedBuildingId || !selectedElementId) return;
    try {
      const insp = await createInspection({ building_id: selectedBuildingId });
      setInspectionId(insp.id);
      setStep(2);
    } catch (err) {
      console.error("Failed to start inspection");
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  const submitImageForAnalysis = async () => {
    if (!imageFile || !inspectionId) return;
    setIsUploading(true);
    try {
      // 1. Upload
      const imgRes = await uploadInspectionImage(inspectionId, imageFile);
      setImageId(imgRes.id);
      
      // 2. Analyze
      const result = await analyzeImage(inspectionId, imgRes.id);
      setAnalysisResult(result);
      setStep(3);
    } catch (err) {
      console.error("Failed to analyze image");
      alert("Failed to upload/analyze image. Please check supported formats and backend connectivity.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSaveDefect = async () => {
    if (!analysisResult || !selectedElementId || !inspectionId || !imageId) return;
    setIsSaving(true);
    try {
      const defect = await createDefect({ 
        defect_type: analysisResult.defect_type, 
        structural_element_id: selectedElementId 
      });
      await createObservation({
        defect_id: defect.id,
        inspection_id: inspectionId,
        image_id: imageId
      });
      navigate(`/defects`);
    } catch (err) {
      console.error("Failed to save defect");
      alert("Failed to save observation.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">New Inspection</h1>
        <p className="text-slate-500">Record a new structural observation in the field.</p>
      </div>

      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>1. Select Structural Location</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Building</label>
              <select 
                className="mt-1 block w-full rounded-md border-slate-300 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white"
                value={selectedBuildingId}
                onChange={(e) => {
                  setSelectedBuildingId(e.target.value);
                  setSelectedFloorId(''); setSelectedAreaId(''); setSelectedElementId('');
                }}
              >
                <option value="">-- Select Building --</option>
                {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>

            {buildingDetail && (
              <div>
                <label className="text-sm font-medium text-slate-700">Floor</label>
                <select 
                  className="mt-1 block w-full rounded-md border-slate-300 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white"
                  value={selectedFloorId}
                  onChange={(e) => {
                    setSelectedFloorId(e.target.value);
                    setSelectedAreaId(''); setSelectedElementId('');
                  }}
                >
                  <option value="">-- Select Floor --</option>
                  {buildingDetail.floors.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
                {/* Real app would allow creating missing hierarchy here, skipping for brevity of shell unless explicitly needed */}
              </div>
            )}

            {selectedFloorId && buildingDetail && (
              <div>
                <label className="text-sm font-medium text-slate-700">Area</label>
                <select 
                  className="mt-1 block w-full rounded-md border-slate-300 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white"
                  value={selectedAreaId}
                  onChange={(e) => {
                    setSelectedAreaId(e.target.value);
                    setSelectedElementId('');
                  }}
                >
                  <option value="">-- Select Area --</option>
                  {buildingDetail.floors.find(f => f.id === selectedFloorId)?.areas.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                </select>
              </div>
            )}

            {selectedAreaId && buildingDetail && (
              <div>
                <label className="text-sm font-medium text-slate-700">Structural Element</label>
                <select 
                  className="mt-1 block w-full rounded-md border-slate-300 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white"
                  value={selectedElementId}
                  onChange={(e) => setSelectedElementId(e.target.value)}
                >
                  <option value="">-- Select Element --</option>
                  {buildingDetail.floors.find(f => f.id === selectedFloorId)?.areas.find(a => a.id === selectedAreaId)?.structural_elements.map(e => <option key={e.id} value={e.id}>{e.name} ({e.element_type})</option>)}
                </select>
              </div>
            )}

            <div className="pt-4 flex justify-end">
              <Button disabled={!selectedElementId} onClick={handleStartInspection}>
                Continue to Image Inspection
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>2. Capture Defect</CardTitle>
            <p className="text-sm text-slate-500">Capture the defect as clearly as possible. Include a scale/reference when physical measurements are required.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-slate-300 rounded-lg p-12 text-center hover:bg-slate-50 transition-colors">
              <UploadCloud className="mx-auto h-12 w-12 text-slate-400 mb-4" />
              <div className="flex text-sm text-slate-600 justify-center">
                <label htmlFor="file-upload" className="relative cursor-pointer rounded-md font-medium text-slate-900 focus-within:outline-none focus-within:ring-2 focus-within:ring-slate-500 focus-within:ring-offset-2 hover:text-slate-700">
                  <span>Upload a file</span>
                  <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/jpeg,image/png,image/webp" onChange={handleImageUpload} />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-slate-500 mt-2">PNG, JPG, WEBP up to 20MB</p>
            </div>
            
            {imageFile && (
              <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-md border border-slate-200">
                <div className="h-16 w-16 bg-slate-200 rounded object-cover overflow-hidden flex-shrink-0">
                  <img src={URL.createObjectURL(imageFile)} alt="Preview" className="h-full w-full object-cover" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">{imageFile.name}</p>
                  <p className="text-xs text-slate-500">{(imageFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            )}

            <div className="pt-4 flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setStep(1)} disabled={isUploading}>Back</Button>
              <Button onClick={submitImageForAnalysis} disabled={!imageFile || isUploading}>
                {isUploading ? 'Validating & Analyzing...' : 'Analyze Image'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 3 && analysisResult && (
        <Card className="border-slate-800">
          <CardHeader className="bg-slate-900 text-white rounded-t-xl">
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-emerald-400" />
              AI-assisted result
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-slate-500">Detected Defect Type</p>
                <p className="text-2xl font-bold capitalize text-slate-900">{analysisResult.defect_type}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">Model Confidence</p>
                <p className="text-2xl font-bold text-slate-900">{(analysisResult.confidence * 100).toFixed(1)}%</p>
              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-md p-4 flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-amber-800">Decision support — engineering review required.</p>
                <p className="text-sm text-amber-700 mt-1">
                  This classification was produced by the {analysisResult.model_name} {analysisResult.model_status} model. 
                  Measurements and severity assessment are currently pending manual engineering review.
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setStep(2)} disabled={isSaving}>Retake Image</Button>
              <Button onClick={handleSaveDefect} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Confirm & Save Observation'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
