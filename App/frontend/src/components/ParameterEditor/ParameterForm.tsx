import React from 'react';
import { Sliders, RefreshCw, Layers } from 'lucide-react';
import { DeviceType } from '../../types';

interface ParameterFormProps {
  deviceType: DeviceType;
  parameters: Record<string, any>;
  onChange: (key: string, value: any) => void;
  onRegenerate: () => void;
  isUpdating: boolean;
}

export const ParameterForm: React.FC<ParameterFormProps> = ({
  deviceType,
  parameters,
  onChange,
  onRegenerate,
  isUpdating,
}) => {
  // Derived calculations
  const wallThickness =
    parameters.outer_diameter_mm && parameters.inner_diameter_mm
      ? (parameters.outer_diameter_mm - parameters.inner_diameter_mm) / 2
      : parameters.body_outer_diameter_mm && parameters.body_inner_diameter_mm
      ? (parameters.body_outer_diameter_mm - parameters.body_inner_diameter_mm) / 2
      : null;

  const frenchSize = parameters.outer_diameter_mm ? parameters.outer_diameter_mm * 3 : null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-sky-400" />
          <h3 className="font-semibold text-white text-base">Parametric Workbench</h3>
        </div>
        <span className="text-xs uppercase font-mono px-2.5 py-1 bg-slate-800 text-sky-400 rounded-md border border-slate-700">
          {deviceType}
        </span>
      </div>

      <div className="mt-4 space-y-4">
        {/* Device-Specific Form Controls */}
        {deviceType === 'tube' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Length (mm): <span className="text-sky-400 font-mono">{parameters.length_mm}</span>
              </label>
              <input
                type="range"
                min="10"
                max="500"
                step="5"
                value={parameters.length_mm || 100}
                onChange={(e) => onChange('length_mm', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Outer Diameter (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.2"
                  max="30"
                  value={parameters.outer_diameter_mm || 3.0}
                  onChange={(e) => onChange('outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Inner Diameter (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max={parameters.outer_diameter_mm ? parameters.outer_diameter_mm - 0.05 : 2.5}
                  value={parameters.inner_diameter_mm || 2.0}
                  onChange={(e) => onChange('inner_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>
            </div>
          </>
        )}

        {deviceType === 'catheter' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Catheter Length (mm): <span className="text-sky-400 font-mono">{parameters.length_mm}</span>
              </label>
              <input
                type="range"
                min="30"
                max="1500"
                step="10"
                value={parameters.length_mm || 150}
                onChange={(e) => onChange('length_mm', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Outer Diameter (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.3"
                  max="15"
                  value={parameters.outer_diameter_mm || 2.0}
                  onChange={(e) => onChange('outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Inner Lumen (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max={parameters.outer_diameter_mm ? parameters.outer_diameter_mm - 0.05 : 1.5}
                  value={parameters.inner_diameter_mm || 1.2}
                  onChange={(e) => onChange('inner_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Tip Length (mm)</label>
                <input
                  type="number"
                  step="0.5"
                  min="1"
                  max="30"
                  value={parameters.tip_length_mm || 5.0}
                  onChange={(e) => onChange('tip_length_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Tip Angle (°)</label>
                <input
                  type="number"
                  step="5"
                  min="0"
                  max="60"
                  value={parameters.tip_angle_deg || 0}
                  onChange={(e) => onChange('tip_angle_deg', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:border-sky-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <input
                type="checkbox"
                id="has_hub"
                checked={parameters.has_luer_hub ?? true}
                onChange={(e) => onChange('has_luer_hub', e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-sky-500 focus:ring-0"
              />
              <label htmlFor="has_hub" className="text-xs text-slate-300 cursor-pointer">
                Include Proximal Luer Connection Hub
              </label>
            </div>
          </>
        )}

        {deviceType === 'tapered_tube' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Length (mm): <span className="text-sky-400 font-mono">{parameters.length_mm}</span>
              </label>
              <input
                type="range"
                min="20"
                max="500"
                step="10"
                value={parameters.length_mm || 120}
                onChange={(e) => onChange('length_mm', parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1">Proximal OD</label>
                <input
                  type="number"
                  step="0.1"
                  value={parameters.proximal_outer_diameter_mm || 4.0}
                  onChange={(e) => onChange('proximal_outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1">Distal OD</label>
                <input
                  type="number"
                  step="0.1"
                  value={parameters.distal_outer_diameter_mm || 2.0}
                  onChange={(e) => onChange('distal_outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1">Inner Lumen</label>
                <input
                  type="number"
                  step="0.1"
                  value={parameters.inner_diameter_mm || 1.2}
                  onChange={(e) => onChange('inner_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-white font-mono"
                />
              </div>
            </div>
          </>
        )}

        {deviceType === 'connector' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Connector Length (mm)</label>
              <input
                type="number"
                step="1"
                min="10"
                max="60"
                value={parameters.length_mm || 20.0}
                onChange={(e) => onChange('length_mm', parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Collar OD (mm)</label>
                <input
                  type="number"
                  step="0.2"
                  value={parameters.outer_diameter_mm || 6.5}
                  onChange={(e) => onChange('outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Fluid Bore (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  value={parameters.inner_diameter_mm || 2.5}
                  onChange={(e) => onChange('inner_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Retention Barbs: <span className="text-sky-400 font-mono">{parameters.barb_count || 2}</span>
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="1"
                value={parameters.barb_count || 2}
                onChange={(e) => onChange('barb_count', parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>
          </>
        )}

        {deviceType === 'injector' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Barrel Length (mm)</label>
              <input
                type="number"
                step="5"
                min="20"
                max="250"
                value={parameters.body_length_mm || 80.0}
                onChange={(e) => onChange('body_length_mm', parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Barrel OD (mm)</label>
                <input
                  type="number"
                  step="0.5"
                  value={parameters.body_outer_diameter_mm || 16.0}
                  onChange={(e) => onChange('body_outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Barrel Bore (mm)</label>
                <input
                  type="number"
                  step="0.5"
                  value={parameters.body_inner_diameter_mm || 14.0}
                  onChange={(e) => onChange('body_inner_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Flange Width (mm)</label>
              <input
                type="number"
                step="1"
                value={parameters.flange_width_mm || 24.0}
                onChange={(e) => onChange('flange_width_mm', parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
              />
            </div>
          </>
        )}

        {deviceType === 'plunger' && (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Plunger Length (mm)</label>
              <input
                type="number"
                step="5"
                min="20"
                max="250"
                value={parameters.plunger_length_mm || 90.0}
                onChange={(e) => onChange('plunger_length_mm', parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Head Sealing OD (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  value={parameters.head_outer_diameter_mm || 13.9}
                  onChange={(e) => onChange('head_outer_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Rod Core OD (mm)</label>
                <input
                  type="number"
                  step="0.5"
                  value={parameters.rod_diameter_mm || 6.0}
                  onChange={(e) => onChange('rod_diameter_mm', parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-white font-mono"
                />
              </div>
            </div>
          </>
        )}

        {/* Live Derived Dimensions Display */}
        <div className="pt-2">
          <div className="bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 text-xs space-y-1.5">
            <div className="text-slate-400 font-medium flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-sky-400" />
              Derived Dimensions (Deterministic):
            </div>
            {wallThickness !== null && (
              <div className="flex justify-between text-slate-300">
                <span>Calculated Wall Thickness:</span>
                <span className="font-mono text-white font-semibold">{wallThickness.toFixed(3)} mm</span>
              </div>
            )}
            {frenchSize !== null && (
              <div className="flex justify-between text-slate-300">
                <span>French Scale (Fr):</span>
                <span className="font-mono text-sky-400 font-semibold">{frenchSize.toFixed(1)} Fr</span>
              </div>
            )}
            {parameters.body_inner_diameter_mm && parameters.body_length_mm && (
              <div className="flex justify-between text-slate-300">
                <span>Usable Volumetric Capacity:</span>
                <span className="font-mono text-emerald-400 font-semibold">
                  {(Math.PI * Math.pow(parameters.body_inner_diameter_mm / 20, 2) * (parameters.body_length_mm / 10)).toFixed(1)} mL
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Regenerate CAD Button */}
        <button
          onClick={onRegenerate}
          disabled={isUpdating}
          className="w-full py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold text-sm rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-sky-500/20 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isUpdating ? 'animate-spin' : ''}`} />
          {isUpdating ? 'Regenerating Solid...' : 'Regenerate Deterministic CAD'}
        </button>
      </div>
    </div>
  );
};
