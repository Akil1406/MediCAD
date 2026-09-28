import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/Layout/Header';
import { DashboardPage } from './pages/DashboardPage';
import { NewDesignPage } from './pages/NewDesignPage';
import { DesignStudioPage } from './pages/DesignStudioPage';
import { VersionHistoryPage } from './pages/VersionHistoryPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/design/new" element={<NewDesignPage />} />
            <Route path="/design/:designId" element={<DesignStudioPage />} />
            <Route path="/design/:designId/history" element={<VersionHistoryPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-400">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>MediCAD • Deterministic Medical Device CAD Prototyping Platform</span>
            <span className="text-slate-400">FastAPI • React • Three.js • LangGraph • CadQuery</span>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
