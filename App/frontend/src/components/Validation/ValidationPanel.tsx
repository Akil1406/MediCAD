import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2, Info } from 'lucide-react';
import { ValidationReport } from '../../types';

interface ValidationPanelProps {
  report?: ValidationReport;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({ report }) => {
  if (!report) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center text-slate-400 text-sm">
        Run CAD generation to inspect Level 1 geometric sanity checks and Level 2 manufacturing design rules.
      </div>
    );
  }

  const errors = report.issues.filter((i) => i.severity === 'ERROR' || i.severity === 'BLOCKED');
  const warnings = report.issues.filter((i) => i.severity === 'WARNING');
  const infos = report.issues.filter((i) => i.severity === 'INFO');

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-sky-400" />
          <h3 className="font-semibold text-white text-base">Geometric & Design Rules Validation</h3>
        </div>

        <div>
          {report.passed ? (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-xs font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              PASSED
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-full text-xs font-semibold">
              <XCircle className="w-3.5 h-3.5" />
              ISSUES DETECTED
            </span>
          )}
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-4 gap-3 mt-4">
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 text-center">
          <div className="text-[11px] text-slate-400 font-medium">Solid Validity</div>
          <div className="text-sm font-semibold text-emerald-400 mt-1">
            {report.solid_valid ? '✓ Manifold' : '✗ Non-manifold'}
          </div>
        </div>

        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 text-center">
          <div className="text-[11px] text-slate-400 font-medium">Wall Thickness</div>
          <div className="text-sm font-mono font-semibold text-white mt-1">
            {report.wall_thickness_mm !== undefined ? `${report.wall_thickness_mm.toFixed(3)} mm` : 'N/A'}
          </div>
        </div>

        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 text-center">
          <div className="text-[11px] text-slate-400 font-medium">Errors / Blockers</div>
          <div className={`text-sm font-mono font-semibold mt-1 ${errors.length > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
            {errors.length}
          </div>
        </div>

        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 text-center">
          <div className="text-[11px] text-slate-400 font-medium">Design Warnings</div>
          <div className={`text-sm font-mono font-semibold mt-1 ${warnings.length > 0 ? 'text-amber-400' : 'text-slate-400'}`}>
            {warnings.length}
          </div>
        </div>
      </div>

      {/* Issues Breakdown List */}
      <div className="mt-5 space-y-2.5">
        {report.issues.length === 0 ? (
          <div className="text-center py-4 text-xs text-slate-400">
            ✓ All Level 1 geometric checks and Level 2 manufacturing constraints passed with zero warnings.
          </div>
        ) : (
          report.issues.map((issue, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border text-xs flex items-start gap-3 ${
                issue.severity === 'ERROR' || issue.severity === 'BLOCKED'
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-200'
                  : issue.severity === 'WARNING'
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-200'
                  : 'bg-sky-500/10 border-sky-500/30 text-sky-200'
              }`}
            >
              {issue.severity === 'ERROR' || issue.severity === 'BLOCKED' ? (
                <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              ) : issue.severity === 'WARNING' ? (
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              ) : (
                <Info className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
              )}

              <div className="flex-1">
                <div className="flex items-center gap-2 font-mono text-[11px] font-semibold opacity-90">
                  <span>[{issue.code}]</span>
                  {issue.parameter && <span className="opacity-75">Param: {issue.parameter}</span>}
                </div>
                <div className="mt-0.5 text-xs font-normal opacity-95">{issue.message}</div>
                {issue.suggested_fix && (
                  <div className="mt-1.5 text-[11px] opacity-80 italic">
                    ↳ Action: {issue.suggested_fix}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
