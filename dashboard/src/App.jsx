import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LiveMap from './views/LiveMap';
import Fleet from './views/Fleet';
import Victims from './views/Victims';
import Hazards from './views/Hazards';
import Sensors from './views/Sensors';
import MissionControl from './views/MissionControl';
import Teleoperation from './views/Teleoperation';
import Analytics from './views/Analytics';
import Playback from './views/Playback';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/map" replace />} />
          <Route path="map" element={<LiveMap />} />
          <Route path="fleet" element={<Fleet />} />
          <Route path="victims" element={<Victims />} />
          <Route path="hazards" element={<Hazards />} />
          <Route path="sensors" element={<Sensors />} />
          <Route path="mission" element={<MissionControl />} />
          <Route path="teleop" element={<Teleoperation />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="playback" element={<Playback />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
