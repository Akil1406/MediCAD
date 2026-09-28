import React, { useState } from 'react';
import { Activity, Play, Gauge, ShieldAlert, Cpu } from 'lucide-react';
import { runSimulation } from '../../services/simulations';
import { SimulationResult, DeviceType } from '../../types';

interface SimulationStudioProps {
  deviceType: DeviceType;
  dimensions: Record<string, any>;
  materialId: string;
}

export const SimulationStudio: React.FC<SimulationStudioProps> = ({
  deviceType,
  dimensions,
  materialId,
}) => {
  const [activeTab, setActiveTab] = useState<'burst_pressure' | 'column_buckling' | 'syringe_dispense_force'>(
    deviceType === 'injector' || deviceType === 'plunger' ? 'syringe_dispense_force' : 'burst_pressure'
  );

  const [operatingPressure, setOperatingPressure] = useState<number>(10.0);
  const [pushForce, setPushForce] = useState<number>(1.5);
  const [flowRate, setFlowRate] = useState<number>(0.5);
  const [viscosity, setViscosity] = useState<number>(1.0);
  const [needleGauge, setNeedleGauge] = useState<number>(23);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setErrorMsg(null);

    try {
      const res = await runSimulation({
        simulation_type: activeTab,
        material_id: materialId || 'MAT_PEBAX_7233',
        operating_pressure_bar: operatingPressure,
        axial_push_force_n: pushForce,
        dispense_flow_rate_ml_s: flowRate,
        fluid_viscosity_cp: viscosity,
        needle_gauge_g: needleGauge,
        custom_dimensions: dimensions,
      });
      setSimResult(res.simulation);
    } catch (err: any) {
      setErrorMsg(err.message || 'Simulation solver encountered an error.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-sky-400" />
          <div>
            <h3 className="font-semibold text-white text-base">Physics Simulation Studio</h3>
            <p className="text-xs text-slate-400">Deterministic structural & fluid mechanical solvers</p>
          </div>
        </div>

        {/* Solver Tabs */}
        <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => {
              setActiveTab('burst_pressure');
              setSimResult(null);
            }}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'burst_pressure' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Burst Pressure (Lamé)
          </button>
          <button
            onClick={() => {
              setActiveTab('column_buckling');
              setSimResult(null);
            }}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'column_buckling' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Column Buckling (Euler)
          </button>
          <button
            onClick={() => {
              setActiveTab('syringe_dispense_force');
              setSimResult(null);
            }}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === 'syringe_dispense_force' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Syringe Flow (Poiseuille)
          </button>
        </div>
      </div>

      {/* Solver Configuration Inputs */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 bg-slate-950/70 p-4 rounded-xl border border-slate-800/80">
        {activeTab === 'burst_pressure' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Internal Pressure: <span className="text-sky-400 font-mono">{operatingPressure} bar</span>
              </label>
              <input
                type="range"
                min="1"
                max="50"
                step="0.5"
                value={operatingPressure}
                onChange={(e) => setOperatingPressure(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>
            <div className="text-xs text-slate-400 sm:col-span-2 flex items-center">
              Evaluates hoop and radial stresses using Lamé thick-wall cylindrical equations against yield strength.
            </div>
          </>
        )}

        {activeTab === 'column_buckling' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Axial Push Force: <span className="text-sky-400 font-mono">{pushForce} N</span>
              </label>
              <input
                type="range"
                min="0.1"
                max="10"
                step="0.1"
                value={pushForce}
                onChange={(e) => setPushForce(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>
            <div className="text-xs text-slate-400 sm:col-span-2 flex items-center">
              Evaluates critical buckling load (P_crit) under axial insertion force using Euler column equations.
            </div>
          </>
        )}

        {activeTab === 'syringe_dispense_force' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Flow Rate: <span className="text-sky-400 font-mono">{flowRate} mL/s</span>
              </label>
              <input
                type="range"
                min="0.1"
                max="5"
                step="0.1"
                value={flowRate}
                onChange={(e) => setFlowRate(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Fluid Viscosity: <span className="text-sky-400 font-mono">{viscosity} cP</span> (Water = 1 cP)
              </label>
              <input
                type="number"
                step="0.5"
                min="0.5"
                max="500"
                value={viscosity}
                onChange={(e) => setViscosity(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Needle Gauge (G)</label>
              <select
                value={needleGauge}
                onChange={(e) => setNeedleGauge(parseInt(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs text-white"
              >
                <option value="18">18G (0.84 mm ID)</option>
                <option value="21">21G (0.51 mm ID)</option>
                <option value="23">23G (0.34 mm ID)</option>
                <option value="25">25G (0.26 mm ID)</option>
                <option value="27">27G (0.21 mm ID)</option>
                <option value="30">30G (0.16 mm ID)</option>
              </select>
            </div>
          </>
        )}

        <div className="sm:col-span-3 flex justify-end">
          <button
            onClick={handleRunSimulation}
            disabled={isRunning}
            className="px-5 py-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold text-xs rounded-lg flex items-center gap-2 shadow-lg shadow-sky-500/20 transition-all disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
            {isRunning ? 'Solving Physics Equations...' : 'Run Simulation Solver'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {errorMsg && (
        <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-300 text-xs">
          {errorMsg}
        </div>
      )}

      {/* Simulation Result Card */}
      {simResult && (
        <div className="mt-5 p-4 rounded-xl border border-slate-800 bg-slate-950 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gauge className="w-4 h-4 text-sky-400" />
              <span className="font-semibold text-white text-sm capitalize">
                {simResult.simulation_type.replace('_', ' ')} Result
              </span>
            </div>

            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold ${
                simResult.status === 'PASS'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : simResult.status === 'WARNING'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              }`}
            >
              {simResult.status}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            {simResult.yield_safety_factor !== undefined && (
              <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400">Yield Safety Factor:</span>
                <div className="text-sm font-mono font-bold text-white mt-0.5">
                  {simResult.yield_safety_factor.toFixed(2)}x
                </div>
              </div>
            )}

            {simResult.theoretical_burst_pressure_bar !== undefined && (
              <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400">Theoretical Burst:</span>
                <div className="text-sm font-mono font-bold text-sky-400 mt-0.5">
                  {simResult.theoretical_burst_pressure_bar.toFixed(1)} bar
                </div>
              </div>
            )}

            {simResult.critical_buckling_load_n !== undefined && (
              <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400">Critical Buckling Load:</span>
                <div className="text-sm font-mono font-bold text-white mt-0.5">
                  {simResult.critical_buckling_load_n.toFixed(2)} N ({simResult.critical_buckling_load_gf?.toFixed(0)} gf)
                </div>
              </div>
            )}

            {simResult.buckling_safety_factor !== undefined && (
              <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400">Buckling SF:</span>
                <div className="text-sm font-mono font-bold text-sky-400 mt-0.5">
                  {simResult.buckling_safety_factor.toFixed(2)}x
                </div>
              </div>
            )}

            {simResult.total_thumb_force_n !== undefined && (
              <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400">Thumb Actuation Force:</span>
                <div className="text-sm font-mono font-bold text-white mt-0.5">
                  {simResult.total_thumb_force_n.toFixed(1)} N ({simResult.total_thumb_force_kgf?.toFixed(2)} kgf)
                </div>
              </div>
            )}

            {simResult.pressure_drop_nozzle_bar !== undefined && (
              <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                <span className="text-slate-400">Nozzle Pressure Drop:</span>
                <div className="text-sm font-mono font-bold text-sky-400 mt-0.5">
                  {simResult.pressure_drop_nozzle_bar.toFixed(2)} bar
                </div>
              </div>
            )}
          </div>

          {/* Solver Summary Assessment */}
          <div className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800/80">
            <strong>Solver Assessment:</strong> {simResult.solver_notes || simResult.ergonomic_assessment}
          </div>
        </div>
      )}
    </div>
  );
};
