import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { History, ArrowLeft, GitCompare, ArrowRight, Layers, FileCode } from 'lucide-react';
import { getDesign } from '../services/designs';
import { DesignSummary, DesignVersion } from '../types';

export const VersionHistoryPage: React.FC = () => {
  const { designId } = useParams<{ designId: string }>();
  const [design, setDesign] = useState<DesignSummary | null>(null);
  const [history, setHistory] = useState<DesignVersion[]>([]);
  const [selectedBaseVer, setSelectedBaseVer] = useState<number>(1);
  const [selectedTargetVer, setSelectedTargetVer] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!designId) return;

    getDesign(designId)
      .then((res) => {
        setDesign(res.design);
        setHistory(res.history);
        if (res.history.length > 1) {
          setSelectedBaseVer(1);
          setSelectedTargetVer(res.history.length);
        } else if (res.history.length === 1) {
          setSelectedBaseVer(1);
          setSelectedTargetVer(1);
        }
      })
      .catch((err) => console.error('Failed to load history:', err))
      .finally(() => setIsLoading(false));
  }, [designId]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-slate-400 text-xs">
        Loading version tree & audit history...
      </div>
    );
  }

  if (!design) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-rose-400 text-xs">
        Design not found.
      </div>
    );
  }

  const verA = history.find((h) => h.version_number === selectedBaseVer);
  const verB = history.find((h) => h.version_number === selectedTargetVer);

  const specA = verA ? (typeof verA.specification_json === 'string' ? JSON.parse(verA.specification_json) : verA.specification_json) : {};
  const specB = verB ? (typeof verB.specification_json === 'string' ? JSON.parse(verB.specification_json) : verB.specification_json) : {};

  const allKeys = Array.from(new Set([...Object.keys(specA), ...Object.keys(specB)])).filter(
    (k) => !['device_type', 'units', 'notes'].includes(k)
  );

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <Link
          to={`/design/${design.design_id}`}
          className="p-2 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg border border-slate-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Immutable Version Tree & Audit Trail
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            {design.title} • {design.design_id}
          </p>
        </div>
      </div>

      {/* Version Timeline */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <History className="w-4 h-4 text-sky-400" />
          <span>Version Revision History ({history.length} versions)</span>
        </h2>

        <div className="space-y-3">
          {history.map((ver) => (
            <div
              key={ver.version_number}
              className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-sky-500/20 text-sky-400 rounded font-mono font-bold text-[11px]">
                    v{ver.version_number}
                  </span>
                  <span className="font-semibold text-white">
                    {ver.user_prompt || 'Parameter Update'}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Created: {new Date(ver.created_at_utc).toLocaleString()} | {ver.app_version}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href={`/api/v1/exports/${design.design_id}/${ver.version_number}/step`}
                  download
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-mono text-[11px] transition-colors"
                >
                  Download .step
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive Parameter Diff Comparator */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <GitCompare className="w-4 h-4 text-sky-400" />
            <h2 className="text-sm font-bold text-white">Parametric Diff Comparator</h2>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Base:</span>
            <select
              value={selectedBaseVer}
              onChange={(e) => setSelectedBaseVer(parseInt(e.target.value))}
              className="bg-slate-950 border border-slate-800 text-white rounded px-2 py-1 font-mono text-xs"
            >
              {history.map((h) => (
                <option key={h.version_number} value={h.version_number}>
                  v{h.version_number}
                </option>
              ))}
            </select>

            <span className="text-slate-400">Target:</span>
            <select
              value={selectedTargetVer}
              onChange={(e) => setSelectedTargetVer(parseInt(e.target.value))}
              className="bg-slate-950 border border-slate-800 text-white rounded px-2 py-1 font-mono text-xs"
            >
              {history.map((h) => (
                <option key={h.version_number} value={h.version_number}>
                  v{h.version_number}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Diff Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-medium uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Parameter</th>
                <th className="py-2.5 px-3 font-mono">v{selectedBaseVer} (Base)</th>
                <th className="py-2.5 px-3 font-mono">v{selectedTargetVer} (Target)</th>
                <th className="py-2.5 px-3 font-mono">Delta</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {allKeys.map((key) => {
                const valA = specA[key];
                const valB = specB[key];
                const isChanged = valA !== valB;
                const delta =
                  typeof valA === 'number' && typeof valB === 'number'
                    ? valB - valA
                    : null;

                return (
                  <tr
                    key={key}
                    className={`hover:bg-slate-800/40 transition-colors ${
                      isChanged ? 'bg-sky-500/10' : ''
                    }`}
                  >
                    <td className="py-2.5 px-3 font-sans font-medium text-slate-200">
                      {key.replace('_', ' ')}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">{valA !== undefined ? `${valA}` : '-'}</td>
                    <td className="py-2.5 px-3 text-white font-semibold">{valB !== undefined ? `${valB}` : '-'}</td>
                    <td className="py-2.5 px-3">
                      {delta !== null ? (
                        <span
                          className={`font-semibold ${
                            delta > 0
                              ? 'text-emerald-400'
                              : delta < 0
                              ? 'text-rose-400'
                              : 'text-slate-400'
                          }`}
                        >
                          {delta > 0 ? `+${delta.toFixed(3)}` : delta.toFixed(3)}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="py-2.5 px-3 font-sans">
                      {isChanged ? (
                        <span className="px-2 py-0.5 bg-sky-500/20 text-sky-400 rounded text-[10px] font-semibold">
                          Modified
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[10px]">Unchanged</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
