import React from 'react';
import { AlertTriangle, Flame, Wind, Building2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { useSensorStore } from '../stores/sensorStore';

const demoHazards = [
  { id: 1, type: 'gas_co', severity: 'critical', x: 5.8, y: -6.3, value: 62, threshold: 50, unit: 'ppm', active: true },
  { id: 2, type: 'fire_active', severity: 'high', x: -3.5, y: 7.0, value: 210, threshold: 150, unit: '°C', active: true },
  { id: 3, type: 'structural_vibration', severity: 'medium', x: 1.2, y: 3.4, value: 0.18, threshold: 0.15, unit: 'g RMS', active: true },
  { id: 4, type: 'gas_nh3', severity: 'low', x: -2.0, y: -1.5, value: 12, threshold: 25, unit: 'ppm', active: true },
  { id: 5, type: 'smoke', severity: 'medium', x: 4.0, y: 4.0, value: 35, threshold: 40, unit: '% vis', active: true },
];

const severityColors = { critical: 'var(--status-critical)', high: 'var(--status-danger)', medium: 'var(--status-warning)', low: 'var(--status-info)' };
const typeIcons = { gas_co: Wind, gas_nh3: Wind, fire_active: Flame, structural_vibration: Building2, smoke: Wind };

export default function Hazards() {
  const { sensorHistory } = useSensorStore();

  return (
    <div className="animate-in">
      <div className="alert-banner critical">
        <AlertTriangle size={18} />
        <strong>CO Level IDLH Exceeded</strong> — 62 ppm at (5.8, -6.3). No-go zone active.
      </div>

      <div className="stats-grid">
        <div className="glass-card"><div className="card-title">Active Hazards</div><div className="card-value danger">{demoHazards.length}</div></div>
        <div className="glass-card"><div className="card-title">Critical</div><div className="card-value danger">{demoHazards.filter(h=>h.severity==='critical').length}</div></div>
        <div className="glass-card"><div className="card-title">No-Go Zones</div><div className="card-value warning">2</div></div>
        <div className="glass-card"><div className="card-title">Gas Sensors</div><div className="card-value accent">4 active</div></div>
      </div>

      <div className="content-grid">
        <div className="glass-card">
          <div className="card-title">CO Concentration Over Time</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={sensorHistory.co_ppm}>
              <defs>
                <linearGradient id="coGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} />
              <YAxis stroke="var(--text-muted)" fontSize={10} />
              <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8, fontSize: '0.8rem' }} />
              <Area type="monotone" dataKey="value" stroke="#ef4444" fill="url(#coGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card">
          <div className="card-title">CO₂ Concentration</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={sensorHistory.co2_ppm}>
              <defs>
                <linearGradient id="co2Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} />
              <YAxis stroke="var(--text-muted)" fontSize={10} />
              <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8 }} />
              <Area type="monotone" dataKey="value" stroke="#3b82f6" fill="url(#co2Grad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card">
        <div className="card-title">Active Hazard Zones</div>
        <table className="data-table">
          <thead>
            <tr><th>Severity</th><th>Type</th><th>Position</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
          </thead>
          <tbody>
            {demoHazards.map((h) => {
              const Icon = typeIcons[h.type] || AlertTriangle;
              return (
                <tr key={h.id}>
                  <td><span style={{ color: severityColors[h.severity], fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem' }}>{h.severity}</span></td>
                  <td><Icon size={14} style={{ marginRight: 6 }} />{h.type.replace('_', ' ')}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>({h.x}, {h.y})</td>
                  <td style={{ fontWeight: 700, color: h.value > h.threshold ? 'var(--status-danger)' : 'var(--text-primary)' }}>{h.value} {h.unit}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{h.threshold} {h.unit}</td>
                  <td><span className="status-dot online" /> Active</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
