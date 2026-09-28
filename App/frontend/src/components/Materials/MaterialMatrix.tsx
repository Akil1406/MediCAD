import React, { useState } from 'react';
import { Database, Filter, Check, Award, ExternalLink, HelpCircle } from 'lucide-react';
import { CandidateScore, Material } from '../../types';

interface MaterialMatrixProps {
  candidates: CandidateScore[];
  onSelectMaterial?: (materialId: string) => void;
  selectedMaterialId?: string;
}

export const MaterialMatrix: React.FC<MaterialMatrixProps> = ({
  candidates,
  onSelectMaterial,
  selectedMaterialId,
}) => {
  const [filterFlexibility, setFilterFlexibility] = useState<string>('all');
  const [filterSterilization, setFilterSterilization] = useState<string>('all');
  const [activeProvenance, setActiveProvenance] = useState<CandidateScore | null>(null);

  const filteredCandidates = candidates.filter((cand) => {
    if (filterFlexibility !== 'all') {
      const e = cand.material.elastic_modulus_mpa;
      if (filterFlexibility === 'flexible' && e >= 200) return false;
      if (filterFlexibility === 'semi_rigid' && (e < 200 || e > 1500)) return false;
      if (filterFlexibility === 'rigid' && e <= 1000) return false;
    }
    if (filterSterilization !== 'all') {
      const sMap = cand.material.sterilization_compatibility;
      const status = sMap[filterSterilization] || '';
      if (!status.toLowerCase().includes('compatible') || status.toLowerCase().includes('not')) {
        return false;
      }
    }
    return true;
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-sky-400" />
          <div>
            <h3 className="font-semibold text-white text-base">Candidate Medical Materials Matrix</h3>
            <p className="text-xs text-slate-400">Multi-factor engineering suitability ranking</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 text-xs">
          <div className="flex items-center gap-1 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterFlexibility}
              onChange={(e) => setFilterFlexibility(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="all">All Flexibilities</option>
              <option value="flexible">Flexible (E &lt; 200 MPa)</option>
              <option value="semi_rigid">Semi-Rigid (200 - 1500 MPa)</option>
              <option value="rigid">Rigid (E &gt; 1000 MPa)</option>
            </select>
          </div>

          <div className="flex items-center gap-1 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
            <select
              value={filterSterilization}
              onChange={(e) => setFilterSterilization(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="all">All Sterilizations</option>
              <option value="EtO">Ethylene Oxide (EtO)</option>
              <option value="Gamma">Gamma Radiation</option>
              <option value="Autoclave">Steam Autoclave</option>
              <option value="E-beam">E-Beam</option>
            </select>
          </div>
        </div>
      </div>

      {/* Materials Table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-medium uppercase tracking-wider text-[10px]">
              <th className="py-2.5 px-3">Material & Grade</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3">Fit Tier</th>
              <th className="py-2.5 px-3">Tensile / Modulus</th>
              <th className="py-2.5 px-3">Sterilization</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-400">
                  No materials match the selected flexibility or sterilization filter criteria.
                </td>
              </tr>
            ) : (
              filteredCandidates.map((cand) => {
                const mat = cand.material;
                const isSelected = selectedMaterialId === mat.material_id;

                return (
                  <tr
                    key={mat.material_id}
                    className={`hover:bg-slate-800/40 transition-colors ${
                      isSelected ? 'bg-sky-500/10 border-l-2 border-l-sky-400' : ''
                    }`}
                  >
                    <td className="py-3 px-3">
                      <div className="font-semibold text-white">{mat.name}</div>
                      <div className="text-[11px] text-slate-400">{mat.common_trade_names.join(', ')}</div>
                    </td>

                    <td className="py-3 px-3 text-slate-300">
                      <div>{mat.category}</div>
                      <div className="text-[10px] text-slate-400 font-mono">ρ = {mat.density_g_cm3} g/cm³</div>
                    </td>

                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold ${
                          cand.engineering_fit === 'Excellent'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : cand.engineering_fit === 'Good'
                            ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        <Award className="w-3 h-3" />
                        {cand.engineering_fit} ({(cand.score * 100).toFixed(0)}%)
                      </span>
                    </td>

                    <td className="py-3 px-3 font-mono text-slate-300">
                      <div>σ_t: <span className="text-white font-semibold">{mat.tensile_strength_mpa.toFixed(1)} MPa</span></div>
                      <div>E: <span className="text-sky-300">{mat.elastic_modulus_mpa.toFixed(0)} MPa</span></div>
                    </td>

                    <td className="py-3 px-3 text-[11px] text-slate-300">
                      <div>EtO: <span className="text-emerald-400">✓</span> | Gamma: <span className="text-emerald-400">✓</span></div>
                      <div className="text-[10px] text-slate-400">Steam: {mat.sterilization_compatibility['Autoclave'] || 'N/A'}</div>
                    </td>

                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setActiveProvenance(cand)}
                          title="View Data Provenance & Citations"
                          className="p-1.5 text-slate-400 hover:text-sky-400 hover:bg-slate-800 rounded transition-colors"
                        >
                          <HelpCircle className="w-4 h-4" />
                        </button>

                        {onSelectMaterial && (
                          <button
                            onClick={() => onSelectMaterial(mat.material_id)}
                            className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                              isSelected
                                ? 'bg-sky-500 text-white'
                                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
                            }`}
                          >
                            {isSelected ? 'Selected' : 'Select'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Provenance Detail Modal */}
      {activeProvenance && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-start justify-between pb-3 border-b border-slate-800">
              <div>
                <h4 className="font-bold text-white text-base">{activeProvenance.material.name}</h4>
                <p className="text-xs text-sky-400 font-mono">{activeProvenance.material.category}</p>
              </div>
              <button
                onClick={() => setActiveProvenance(null)}
                className="text-slate-400 hover:text-white text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <span className="font-semibold text-white">ISO 10993 Reference:</span>
                <p className="text-slate-400 mt-0.5">{activeProvenance.material.iso_10993_biocompatibility_reference}</p>
              </div>

              <div>
                <span className="font-semibold text-white">Engineering Provenance & Source:</span>
                <p className="text-slate-400 mt-0.5">{activeProvenance.evidence_provenance}</p>
              </div>

              <div>
                <span className="font-semibold text-white">Standard Medical Applications:</span>
                <ul className="list-disc list-inside text-slate-400 mt-1 space-y-0.5">
                  {activeProvenance.material.typical_medical_applications.map((app, i) => (
                    <li key={i}>{app}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-[11px] text-amber-300/90">
                <strong>Disclaimer:</strong> {activeProvenance.regulatory_disclaimer}
              </div>
            </div>

            <div className="pt-2 text-right">
              <button
                onClick={() => setActiveProvenance(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
