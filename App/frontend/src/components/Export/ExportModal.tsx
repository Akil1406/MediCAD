import React, { useState } from 'react';
import { Download, FileCode, Layers, FileText, CheckSquare, Square, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface ExportModalProps {
  designId: string;
  version: number;
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  designId,
  version,
  isOpen,
  onClose,
}) => {
  const [acknowledged, setAcknowledged] = useState(false);

  if (!isOpen) return null;

  const downloadStepUrl = `/api/v1/exports/${designId}/${version}/step`;
  const downloadStlUrl = `/api/v1/exports/${designId}/${version}/stl`;
  const downloadReportUrl = `/api/v1/exports/${designId}/${version}/report`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="flex items-start justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Download className="w-5 h-5 text-sky-400" />
            <div>
              <h3 className="font-bold text-white text-lg">Export CAD Design Package</h3>
              <p className="text-xs text-slate-400 font-mono">
                {designId} • Version v{version}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-sm font-semibold"
          >
            ✕
          </button>
        </div>

        {/* Regulatory Warning & Acknowledgment Gate */}
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 text-xs text-amber-200/90 space-y-3">
          <div className="flex items-center gap-2 font-semibold text-amber-300">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Safety & Regulatory Disclaimer</span>
          </div>
          <p className="leading-relaxed text-[11px] text-amber-200/80">
            All exported geometry (STEP, STL) and engineering reports are generated for engineering prototyping and mechanical feasibility purposes only. They are NOT certified for in-vivo clinical use, surgical implantation, sterility validation, or human trials.
          </p>

          <label className="flex items-center gap-2.5 pt-1 text-xs text-white font-medium cursor-pointer">
            <input
              type="checkbox"
              checked={acknowledged}
              onChange={(e) => setAcknowledged(e.target.checked)}
              className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-sky-500 focus:ring-0 cursor-pointer"
            />
            <span>I acknowledge this artifact is for engineering prototyping only</span>
          </label>
        </div>

        {/* Download Action Cards */}
        <div className="space-y-2.5">
          <a
            href={acknowledged ? downloadStepUrl : undefined}
            download
            className={`p-3 rounded-lg border flex items-center justify-between transition-all ${
              acknowledged
                ? 'bg-slate-950 hover:bg-slate-800 border-slate-800 text-white cursor-pointer group'
                : 'bg-slate-950/50 border-slate-800/50 text-slate-500 cursor-not-allowed'
            }`}
          >
            <div className="flex items-center gap-3">
              <FileCode className={`w-5 h-5 ${acknowledged ? 'text-sky-400' : 'text-slate-600'}`} />
              <div>
                <div className="font-semibold text-xs text-white">ISO 10303-21 STEP CAD Model</div>
                <div className="text-[10px] text-slate-400">Authoritative B-Rep parametric geometry file (.step)</div>
              </div>
            </div>
            <Download className={`w-4 h-4 ${acknowledged ? 'text-slate-400 group-hover:text-white' : 'text-slate-600'}`} />
          </a>

          <a
            href={acknowledged ? downloadStlUrl : undefined}
            download
            className={`p-3 rounded-lg border flex items-center justify-between transition-all ${
              acknowledged
                ? 'bg-slate-950 hover:bg-slate-800 border-slate-800 text-white cursor-pointer group'
                : 'bg-slate-950/50 border-slate-800/50 text-slate-500 cursor-not-allowed'
            }`}
          >
            <div className="flex items-center gap-3">
              <Layers className={`w-5 h-5 ${acknowledged ? 'text-sky-400' : 'text-slate-600'}`} />
              <div>
                <div className="font-semibold text-xs text-white">Triangulated STL Mesh Preview</div>
                <div className="text-[10px] text-slate-400">Rapid prototyping & 3D viewer mesh (.stl)</div>
              </div>
            </div>
            <Download className={`w-4 h-4 ${acknowledged ? 'text-slate-400 group-hover:text-white' : 'text-slate-600'}`} />
          </a>

          <a
            href={acknowledged ? downloadReportUrl : undefined}
            download
            className={`p-3 rounded-lg border flex items-center justify-between transition-all ${
              acknowledged
                ? 'bg-slate-950 hover:bg-slate-800 border-slate-800 text-white cursor-pointer group'
                : 'bg-slate-950/50 border-slate-800/50 text-slate-500 cursor-not-allowed'
            }`}
          >
            <div className="flex items-center gap-3">
              <FileText className={`w-5 h-5 ${acknowledged ? 'text-sky-400' : 'text-slate-600'}`} />
              <div>
                <div className="font-semibold text-xs text-white">Full Engineering Report</div>
                <div className="text-[10px] text-slate-400">Specification, validation rules & material provenance (.md)</div>
              </div>
            </div>
            <Download className={`w-4 h-4 ${acknowledged ? 'text-slate-400 group-hover:text-white' : 'text-slate-600'}`} />
          </a>
        </div>

        {/* Footer */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
