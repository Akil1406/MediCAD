import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Download,
  History,
  ShieldCheck,
  Database,
  Activity,
  Box,
  Layers,
  ArrowLeft,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { getDesign, updateDesignParameters } from '../services/designs';
import { buildCadModel } from '../services/cad';
import { ThreeViewer } from '../components/CadViewer/ThreeViewer';
import { ParameterForm } from '../components/ParameterEditor/ParameterForm';
import { ValidationPanel } from '../components/Validation/ValidationPanel';
import { MaterialMatrix } from '../components/Materials/MaterialMatrix';
import { SimulationStudio } from '../components/Simulation/SimulationStudio';
import { ExportModal } from '../components/Export/ExportModal';
import { DesignSummary, DesignVersion, CADProperties, ValidationReport, CandidateScore, DeviceType } from '../types';

export const DesignStudioPage: React.FC = () => {
  const { designId } = useParams<{ designId: string }>();

  const [design, setDesign] = useState<DesignSummary | null>(null);
  const [currentVersion, setCurrentVersion] = useState<DesignVersion | null>(null);
  const [history, setHistory] = useState<DesignVersion[]>([]);

  // Working state
  const [deviceType, setDeviceType] = useState<DeviceType>('catheter');
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [cadProperties, setCadProperties] = useState<CADProperties | undefined>();
  const [stlBase64, setStlBase64] = useState<string | undefined>();
  const [validationReport, setValidationReport] = useState<ValidationReport | undefined>();
  const [materialCandidates, setMaterialCandidates] = useState<CandidateScore[]>([]);
  const [selectedMaterialId, setSelectedMaterialId] = useState<string>('MAT_PEBAX_7233');

  const [activeTab, setActiveTab] = useState<'validation' | 'materials' | 'simulation' | 'history'>('validation');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  useEffect(() => {
    if (!designId) return;

    setIsLoading(true);
    getDesign(designId)
      .then((res) => {
        setDesign(res.design);
        setCurrentVersion(res.latest_version);
        setHistory(res.history);

        const dtype = res.design.device_type as DeviceType;
        setDeviceType(dtype);

        const spec = typeof res.latest_version.specification_json === 'string'
          ? JSON.parse(res.latest_version.specification_json)
          : res.latest_version.specification_json;
        setParameters(spec);

        const cad = typeof res.latest_version.cad_properties_json === 'string'
          ? JSON.parse(res.latest_version.cad_properties_json)
          : res.latest_version.cad_properties_json;
        setCadProperties(cad);

        const val = typeof res.latest_version.validation_json === 'string'
          ? JSON.parse(res.latest_version.validation_json)
          : res.latest_version.validation_json;
        setValidationReport(val);

        const mats = typeof res.latest_version.material_candidates_json === 'string'
          ? JSON.parse(res.latest_version.material_candidates_json)
          : res.latest_version.material_candidates_json;
        setMaterialCandidates(mats || []);

        // Initial preview build
        buildCadModel(spec).then((cadRes) => {
          setStlBase64(cadRes.stl_base64);
        });
      })
      .catch((err) => console.error('Failed to load design:', err))
      .finally(() => setIsLoading(false));
  }, [designId]);

  const handleParameterChange = (key: string, value: any) => {
    setParameters((prev) => ({ ...prev, [key]: value }));
  };

  const handleRegenerateCAD = async () => {
    if (!designId) return;
    setIsUpdating(true);

    try {
      const res = await updateDesignParameters(designId, {
        parameters,
        prompt: 'Manual parameter adjustment via Workbench',
      });

      // Update state with new immutable version
      setDesign((prev) => (prev ? { ...prev, latest_version: res.version } : null));
      setParameters(res.specification);
      setCadProperties(res.cad_properties);
      setValidationReport(res.validation);
      setMaterialCandidates(res.material_candidates || []);
      setStlBase64(res.mesh_stl_bytes);
    } catch (err: any) {
      console.error('Failed to update design parameters:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-slate-400 text-sm">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-sky-400" />
        Loading CAD model & engineering parameters...
      </div>
    );
  }

  if (!design) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-rose-400 text-sm">
        Design project not found.
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="p-2 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg border border-slate-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">{design.title}</h1>
              <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full font-mono text-xs font-semibold">
                v{design.latest_version}
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
              <span className="font-mono">{design.design_id}</span>
              <span>•</span>
              <span className="uppercase font-semibold text-sky-400">{deviceType}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to={`/design/${design.design_id}/history`}
            className="px-3 py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <History className="w-4 h-4 text-slate-400" />
            <span>Version Tree</span>
          </Link>

          <button
            onClick={() => setIsExportOpen(true)}
            className="px-4 py-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-lg shadow-sky-500/20 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Export CAD Package</span>
          </button>
        </div>
      </div>

      {/* Main 3D Viewport & Parameter Controls Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left/Center: Three.js 3D Viewport */}
        <div className="lg:col-span-7 space-y-3">
          <ThreeViewer
            stlBase64={stlBase64}
            cadProperties={cadProperties}
            height={520}
          />
        </div>

        {/* Right: Dynamic Parametric Workbench */}
        <div className="lg:col-span-5">
          <ParameterForm
            deviceType={deviceType}
            parameters={parameters}
            onChange={handleParameterChange}
            onRegenerate={handleRegenerateCAD}
            isUpdating={isUpdating}
          />
        </div>
      </div>

      {/* Bottom Tabbed Engineering Analysis Studio */}
      <div className="space-y-4">
        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('validation')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors ${
              activeTab === 'validation'
                ? 'bg-slate-800 text-sky-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Geometric & Manufacturing Rules</span>
          </button>

          <button
            onClick={() => setActiveTab('materials')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors ${
              activeTab === 'materials'
                ? 'bg-slate-800 text-sky-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Medical Materials Ranking</span>
          </button>

          <button
            onClick={() => setActiveTab('simulation')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors ${
              activeTab === 'simulation'
                ? 'bg-slate-800 text-sky-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Physics Simulations</span>
          </button>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'validation' && (
            <ValidationPanel report={validationReport} />
          )}

          {activeTab === 'materials' && (
            <MaterialMatrix
              candidates={materialCandidates}
              selectedMaterialId={selectedMaterialId}
              onSelectMaterial={(matId) => setSelectedMaterialId(matId)}
            />
          )}

          {activeTab === 'simulation' && (
            <SimulationStudio
              deviceType={deviceType}
              dimensions={parameters}
              materialId={selectedMaterialId}
            />
          )}
        </div>
      </div>

      {/* Export CAD Package Modal */}
      <ExportModal
        designId={design.design_id}
        version={design.latest_version}
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
      />
    </div>
  );
};
