import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Map, Users, AlertTriangle, Radio, Activity,
  Gamepad2, BarChart3, PlayCircle, Shield, Cpu
} from 'lucide-react';
import { useMissionStore } from '../../stores/missionStore';

const navSections = [
  {
    title: 'Operations',
    items: [
      { to: '/map', label: 'Live Map', icon: Map },
      { to: '/mission', label: 'Mission Control', icon: Shield },
      { to: '/teleop', label: 'Teleoperation', icon: Gamepad2 },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { to: '/victims', label: 'Survivors', icon: Users, badgeKey: 'victims' },
      { to: '/hazards', label: 'Hazards', icon: AlertTriangle, badgeKey: 'hazards' },
      { to: '/sensors', label: 'IoT Nodes', icon: Radio },
    ],
  },
  {
    title: 'Fleet & Analysis',
    items: [
      { to: '/fleet', label: 'Fleet', icon: Cpu },
      { to: '/analytics', label: 'Analytics', icon: BarChart3 },
      { to: '/playback', label: 'Playback', icon: PlayCircle },
    ],
  },
];

export default function Sidebar() {
  const { victimsConfirmed, hazardsDetected } = useMissionStore();
  const badges = { victims: victimsConfirmed, hazards: hazardsDetected };

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>⚡ DisasterMap</h1>
        <div className="subtitle">Command Center</div>
      </div>

      <nav className="sidebar-nav">
        {navSections.map((section) => (
          <div key={section.title} className="sidebar-section">
            <div className="sidebar-section-title">{section.title}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <item.icon className="nav-icon" />
                <span>{item.label}</span>
                {item.badgeKey && badges[item.badgeKey] > 0 && (
                  <span className="nav-badge">{badges[item.badgeKey]}</span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-status">
        <div className="status-row">
          <span className="label">
            <span className="status-dot online" />
            MQTT
          </span>
          <span className="value">Connected</span>
        </div>
        <div className="status-row">
          <span className="label">
            <span className="status-dot online" />
            Robot 1
          </span>
          <span className="value">Active</span>
        </div>
        <div className="status-row">
          <span className="label">Radio</span>
          <span className="value" style={{ color: 'var(--accent-cyan)' }}>-42 dBm</span>
        </div>
      </div>
    </aside>
  );
}
