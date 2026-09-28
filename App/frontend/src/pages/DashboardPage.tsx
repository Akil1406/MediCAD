import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  PlusCircle,
  FileCode,
  ShieldCheck,
  Database,
  ArrowRight,
  Sparkles,
  Layers,
  Activity,
  Box,
} from 'lucide-react';
import { listDesigns } from '../services/designs';
import { DesignSummary } from '../types';

export const DashboardPage: React.FC = () => {
  const [designs, setDesigns] = useState<DesignSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    listDesigns()
      .then((res) => setDesigns(res.designs))
      .catch((err) => console.error('Failed to list designs:', err))
      .finally(() => setIsLoading(false));
  }, []);

  const templates = [
    {
      type: 'catheter',
      title: 'Vascular Catheter Shaft',
      desc: 'Thin-wall multi-lumen / single-lumen shaft with distal tapered tip & Luer hub.',
      icon: '🩺',
      color: 'from-sky-500/20 to-blue-600/20 border-sky-500/30',
    },
    {
      type: 'tube',
      title: 'Precision Micro-Tube',
      desc: 'Extruded medical polymer/metal straight conduit with strict wall tolerances.',
      icon: '📏',
      color: 'from-blue-500/20 to-indigo-600/20 border-blue-500/30',
    },
    {
      type: 'tapered_tube',
      title: 'Tapered Introducer Shaft',
      desc: 'Continuous conical transition between proximal hub and atraumatic distal tip.',
      icon: '📐',
      color: 'from-indigo-500/20 to-violet-600/20 border-indigo-500/30',
    },
    {
      type: 'connector',
      title: 'ISO 80369 Luer Fitting',
      desc: 'Standard 6% conical male/female Luer lock connector with retention barbs.',
      icon: '🔗',
      color: 'from-emerald-500/20 to-teal-600/20 border-emerald-500/30',
    },
    {
      type: 'injector',
      title: 'Syringe Dispense Barrel',
      desc: 'Precision hydraulic syringe cylinder with finger flange & distal nozzle.',
      icon: '💉',
      color: 'from-amber-500/20 to-orange-600/20 border-amber-500/30',
    },
    {
      type: 'plunger',
      title: 'Elastomeric Plunger Piston',
      desc: 'Ribbed sealing stopper head with structural thumb depression rod.',
      icon: '🔘',
      color: 'from-purple-500/20 to-pink-600/20 border-purple-500/30',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Banner */}
      <div className="relative rounded-2xl overflow-hidden bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border border-slate-800 p-8 shadow-2xl">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-sky-500/10 border border-sky-500/30 rounded-full text-xs font-semibold text-sky-400">
            <Sparkles className="w-3.5 h-3.5" />
            Parametric Medical CAD Prototyping Platform
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Deterministic Medical Tool Engineering Studio
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Translate clinical design intent into verified 3D CAD geometry (STEP & STL), execute Level 1/2 manufacturing rule checks, score medical-grade materials, and simulate structural pushability.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Link
              to="/design/new"
              className="px-5 py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-sky-500/20 flex items-center gap-2 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              Launch New Design Studio
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">CAD Projects</span>
            <Box className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2 font-mono">{designs.length}</div>
          <span className="text-[11px] text-slate-400">Immutable versions stored</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Rule Validation</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2 font-mono">100%</div>
          <span className="text-[11px] text-emerald-400">Level 1 & Level 2 active</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Medical Materials</span>
            <Database className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2 font-mono">10 Grades</div>
          <span className="text-[11px] text-slate-400">ISO 10993 referenced</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Physics Solvers</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2 font-mono">3 Solvers</div>
          <span className="text-[11px] text-slate-400">Burst, Buckling, Poiseuille</span>
        </div>
      </div>

      {/* Quick Start Templates */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-tight">Parametric Template Blueprints</h2>
          <span className="text-xs text-slate-400">Select a device archetype to start</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((tpl) => (
            <Link
              key={tpl.type}
              to={`/design/new?type=${tpl.type}`}
              className={`p-5 rounded-xl border bg-gradient-to-br ${tpl.color} hover:border-sky-400/60 transition-all group flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl">{tpl.icon}</span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 bg-slate-900/60 rounded text-slate-300">
                    {tpl.type}
                  </span>
                </div>
                <h3 className="font-bold text-white text-base mt-3 group-hover:text-sky-300 transition-colors">
                  {tpl.title}
                </h3>
                <p className="text-xs text-slate-300/80 mt-1 leading-relaxed">{tpl.desc}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-sky-400 font-medium">
                <span>Configure CAD</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Projects Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h2 className="text-base font-bold text-white">Recent Design Projects</h2>
          <span className="text-xs text-slate-400">{designs.length} designs in local repository</span>
        </div>

        {isLoading ? (
          <div className="text-center py-8 text-xs text-slate-400">Loading CAD models...</div>
        ) : designs.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400 space-y-2">
            <div>No designs created yet. Launch the studio to generate your first medical CAD model.</div>
            <Link
              to="/design/new"
              className="inline-flex items-center gap-1.5 text-sky-400 hover:text-sky-300 font-semibold text-xs"
            >
              <PlusCircle className="w-3.5 h-3.5" /> Start New Design
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-medium uppercase tracking-wider text-[10px]">
                  <th className="py-2.5 px-3">Design Title & ID</th>
                  <th className="py-2.5 px-3">Archetype</th>
                  <th className="py-2.5 px-3">Latest Version</th>
                  <th className="py-2.5 px-3">Created</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {designs.map((d) => (
                  <tr key={d.design_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-semibold text-white">{d.title}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{d.design_id}</div>
                    </td>

                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 bg-slate-800 text-sky-300 rounded font-mono text-[11px]">
                        {d.device_type}
                      </span>
                    </td>

                    <td className="py-3 px-3 font-mono text-slate-300">
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[11px] font-semibold">
                        v{d.latest_version}
                      </span>
                    </td>

                    <td className="py-3 px-3 text-slate-400 text-[11px]">
                      {new Date(d.created_at_utc).toLocaleString()}
                    </td>

                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/design/${d.design_id}`}
                        className="px-3 py-1.5 bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded-lg text-xs font-semibold inline-flex items-center gap-1 transition-colors"
                      >
                        Open Studio <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
