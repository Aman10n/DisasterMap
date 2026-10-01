import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';

const LiveMap = lazy(() => import('./views/LiveMap'));
const Fleet = lazy(() => import('./views/Fleet'));
const Victims = lazy(() => import('./views/Victims'));
const Hazards = lazy(() => import('./views/Hazards'));
const Sensors = lazy(() => import('./views/Sensors'));
const MissionControl = lazy(() => import('./views/MissionControl'));
const Teleoperation = lazy(() => import('./views/Teleoperation'));
const Analytics = lazy(() => import('./views/Analytics'));
const Playback = lazy(() => import('./views/Playback'));

function LoadingView() {
  return (
    <div className="glass-card" role="status" aria-live="polite">
      Loading mission view…
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/map" replace />} />
          <Route path="map" element={<Suspense fallback={<LoadingView />}><LiveMap /></Suspense>} />
          <Route path="fleet" element={<Suspense fallback={<LoadingView />}><Fleet /></Suspense>} />
          <Route path="victims" element={<Suspense fallback={<LoadingView />}><Victims /></Suspense>} />
          <Route path="hazards" element={<Suspense fallback={<LoadingView />}><Hazards /></Suspense>} />
          <Route path="sensors" element={<Suspense fallback={<LoadingView />}><Sensors /></Suspense>} />
          <Route path="mission" element={<Suspense fallback={<LoadingView />}><MissionControl /></Suspense>} />
          <Route path="teleop" element={<Suspense fallback={<LoadingView />}><Teleoperation /></Suspense>} />
          <Route path="analytics" element={<Suspense fallback={<LoadingView />}><Analytics /></Suspense>} />
          <Route path="playback" element={<Suspense fallback={<LoadingView />}><Playback /></Suspense>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
