import React from 'react';
import { useLocation } from 'react-router-dom';
import { Clock, Wifi } from 'lucide-react';
import { useMissionStore } from '../../stores/missionStore';

const routeTitles = {
  '/map': 'Live Environment Map',
  '/fleet': 'Fleet Management',
  '/victims': 'Survivor Detection Board',
  '/hazards': 'Hazard Map & Alerts',
  '/sensors': 'IoT Sensor Nodes',
  '/mission': 'Mission Control',
  '/teleop': 'Teleoperation',
  '/analytics': 'Mission Analytics',
  '/playback': 'Mission Playback',
};

export default function Header() {
  const location = useLocation();
  const { missionState, missionName } = useMissionStore();
  const title = routeTitles[location.pathname] || 'DisasterMap';

  const stateClass = missionState === 'EXPLORING' ? 'state-exploring'
    : missionState === 'HAZARD_RESPONSE' ? 'state-hazard'
    : 'state-idle';

  return (
    <header className="header">
      <h2 className="header-title">{title}</h2>
      <div className="header-actions">
        <div className={`header-badge ${stateClass}`}>
          <span className="status-dot online" />
          {missionState || 'IDLE'}
        </div>
        {missionName && (
          <div className="header-badge state-idle">{missionName}</div>
        )}
        <div className="header-badge state-idle">
          <Clock size={12} />
          {new Date().toLocaleTimeString()}
        </div>
      </div>
    </header>
  );
}
