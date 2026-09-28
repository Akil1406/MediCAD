import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Sparkles, Sliders, ArrowRight, CheckCircle2, RefreshCw, AlertTriangle } from 'lucide-react';
import { createDesign } from '../services/designs';
import { runAiAgent } from '../services/ai';
import { ThreeViewer } from '../components/CadViewer/ThreeViewer';
import { DeviceType } from '../types';

export const NewDesignPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialType = (searchParams.get('type') as DeviceType) || 'catheter';

  const [mode, setMode] = useState<'ai' | 'template'>('ai');
  const [deviceType, setDeviceType] = useState<DeviceType>(initialType);
  const [title, setTitle] = useState<string>('Coronary Micro-Catheter Prototype');
  const [aiPrompt, setAiPrompt] = useState<string>(
    'Design a vascular catheter shaft 150 mm long, 2.0 mm outer diameter, 1.2 mm inner lumen, with a 5 mm distal atraumatic tip.'
  );

  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleCreate = async () => {
    setIsProcessing(true);
    setErrorMessage(null);

    try {
      if (mode === 'ai') {
        const res = await createDesign({
          title: title || 'AI Medical CAD Model',
          device_type: deviceType,
          prompt: aiPrompt,
        });
        navigate(`/design/${res.design_id}`);
      } else {
        const res = await createDesign({
          title: title || `${deviceType.toUpperCase()} Model`,
          device_type: deviceType,
        });
        navigate(`/design/${res.design_id}`);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create design model.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Header */}
      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          New Medical Device CAD Studio
        </h1>
        <p className="text-sm text-slate-400">
          Initialize a new parametric CAD model using AI natural-language extraction or calibrated archetypes.
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex items-center gap-3 p-1 bg-slate-900 rounded-xl border border-slate-800">
        <button
          onClick={() => setMode('ai')}
          className={`flex-1 py-3 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 transition-all ${
            mode === 'ai'
              ? 'bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-md shadow-sky-500/20'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>AI Natural-Language Intake</span>
        </button>

        <button
          onClick={() => setMode('template')}
          className={`flex-1 py-3 px-4 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 transition-all ${
            mode === 'template'
              ? 'bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-md shadow-sky-500/20'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>Template Archetype Selector</span>
        </button>
      </div>

      {/* Main Configuration Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Project Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Coronary Micro-Catheter Prototype"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-sky-500 focus:outline-none font-medium"
          />
        </div>

        {mode === 'ai' ? (
          <div className="space-y-3">
            <label className="block text-xs font-semibold text-slate-300">
              Clinical & Engineering Prompt
            </label>
            <textarea
              rows={4}
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Describe target dimensions, catheter length, lumen ID, tip angles, or syringe volumes..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs sm:text-sm text-white focus:border-sky-500 focus:outline-none leading-relaxed font-sans"
            />
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="font-semibold text-sky-400">Example Prompts:</span>
              <button
                onClick={() =>
                  setAiPrompt('Vascular catheter 160 mm long, 2.0 mm outer diameter, 1.2 mm inner lumen, 5 mm atraumatic tip.')
                }
                className="underline hover:text-slate-200"
              >
                Catheter (160mm)
              </button>
              •
              <button
                onClick={() =>
                  setAiPrompt('Syringe barrel with 80 mm body length, 16 mm outer diameter, 14 mm bore, and 24 mm finger flange.')
                }
                className="underline hover:text-slate-200"
              >
                Syringe Barrel
              </button>
              •
              <button
                onClick={() =>
                  setAiPrompt('Extruded straight micro-tube 100 mm long, 3.0 mm OD, 2.0 mm ID.')
                }
                className="underline hover:text-slate-200"
              >
                Micro-Tube
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <label className="block text-xs font-semibold text-slate-300">
              Select Device Archetype
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[
                { id: 'catheter', name: 'Catheter Shaft', icon: '🩺' },
                { id: 'tube', name: 'Straight Tube', icon: '📏' },
                { id: 'tapered_tube', name: 'Tapered Shaft', icon: '📐' },
                { id: 'connector', name: 'Luer Connector', icon: '🔗' },
                { id: 'injector', name: 'Syringe Barrel', icon: '💉' },
                { id: 'plunger', name: 'Plunger Piston', icon: '🔘' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setDeviceType(item.id as DeviceType)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    deviceType === item.id
                      ? 'bg-sky-500/20 border-sky-500 text-white'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <div className="text-xl">{item.icon}</div>
                  <div className="font-semibold text-xs mt-2 text-white">{item.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-0.5">{item.id}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Submit & Generate */}
        <div className="pt-2">
          <button
            onClick={handleCreate}
            disabled={isProcessing}
            className="w-full py-3.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-sky-500/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Executing LangGraph Orchestrator & Deterministic CAD Engine...</span>
              </>
            ) : (
              <>
                <span>Generate CAD & Open Workbench</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
