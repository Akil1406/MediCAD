import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Stethoscope, Sparkles, PlusCircle, LayoutDashboard, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const Header: React.FC = () => {
  const location = useLocation();
  const [backendHealth, setBackendHealth] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    fetch('/health')
      .then((res) => {
        if (res.ok) setBackendHealth('online');
        else setBackendHealth('offline');
      })
      .catch(() => setBackendHealth('offline'));
  }, []);

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      {/* Top Warning Banner */}
      <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 text-xs text-amber-300/90 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-5xl mx-auto truncate">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>
            <strong>ENGINEERING PROTOTYPING AID:</strong> Outputs are not clinical advice and are not certified for medical in-vivo use or patient treatment.
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] shrink-0">
          <span className="text-slate-400">Backend:</span>
          {backendHealth === 'online' ? (
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <CheckCircle2 className="w-3 h-3" /> FastAPI 8000
            </span>
          ) : (
            <span className="text-rose-400 font-medium">Connecting...</span>
          )}
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
              <Stethoscope className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white tracking-tight">MediCAD</span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded-full">
                  FastAPI + React
                </span>
              </div>
              <p className="text-xs text-slate-400 -mt-0.5">Parametric Medical Device Prototyping</p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
            <Link
              to="/"
              className={`px-3.5 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                isActive('/')
                  ? 'bg-slate-800 text-sky-400 font-semibold'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
            <Link
              to="/design/new"
              className={`px-3.5 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                isActive('/design/new')
                  ? 'bg-slate-800 text-sky-400 font-semibold'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <PlusCircle className="w-4 h-4" />
              New Design Studio
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/design/new"
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-sky-500 to-blue-600 text-white text-sm font-semibold hover:from-sky-400 hover:to-blue-500 shadow-md shadow-sky-500/20 flex items-center gap-2 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>AI Design Intake</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
