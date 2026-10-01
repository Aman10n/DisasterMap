import React from 'react';
import { BarChart3, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend } from 'recharts';

const coverageData = [
  { time: '0m', area: 0 }, { time: '5m', area: 12 }, { time: '10m', area: 31 },
  { time: '15m', area: 52 }, { time: '20m', area: 71 }, { time: '25m', area: 89 },
  { time: '30m', area: 104 }, { time: '35m', area: 115 }, { time: '40m', area: 123 },
  { time: '45m', area: 127 },
];

const modalityPerf = [
  { modality: 'Thermal', precision: 92, recall: 88, latency: 1.2 },
  { modality: 'Acoustic', precision: 78, recall: 71, latency: 3.5 },
  { modality: 'CO₂', precision: 65, recall: 82, latency: 8.2 },
  { modality: 'Visual', precision: 95, recall: 85, latency: 0.8 },
];

const radarData = [
  { metric: 'Coverage', value: 88 }, { metric: 'Speed', value: 75 },
  { metric: 'Accuracy', value: 92 }, { metric: 'Detection', value: 85 },
  { metric: 'Energy Eff.', value: 70 }, { metric: 'SLAM Quality', value: 95 },
];

export default function Analytics() {
  return (
    <div className="animate-in">
      <div className="stats-grid">
        <div className="glass-card"><div className="card-title">Total Area</div><div className="card-value accent">127.4 m²</div></div>
        <div className="glass-card"><div className="card-title">Exploration Rate</div><div className="card-value accent">4.2 m²/min</div></div>
        <div className="glass-card"><div className="card-title">SLAM Error</div><div className="card-value">0.08 m</div></div>
        <div className="glass-card"><div className="card-title">Energy</div><div className="card-value">2.1 Wh/m²</div></div>
      </div>

      <div className="content-grid">
        <div className="glass-card">
          <div className="card-title">Coverage Progress</div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={coverageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)"/>
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10}/>
              <YAxis stroke="var(--text-muted)" fontSize={10}/>
              <Tooltip contentStyle={{background:'var(--bg-secondary)',border:'1px solid var(--glass-border)',borderRadius:8}}/>
              <Bar dataKey="area" fill="url(#barGrad)" radius={[4,4,0,0]}/>
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06d6a0"/>
                  <stop offset="100%" stopColor="#118ab2"/>
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card">
          <div className="card-title">Mission Performance Radar</div>
          <ResponsiveContainer width="100%" height={250}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.1)"/>
              <PolarAngleAxis dataKey="metric" tick={{fill:'var(--text-secondary)',fontSize:11}}/>
              <Radar dataKey="value" stroke="#06d6a0" fill="#06d6a0" fillOpacity={0.2} strokeWidth={2}/>
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card">
        <div className="card-title">Detection Modality Performance</div>
        <table className="data-table">
          <thead><tr><th>Modality</th><th>Precision</th><th>Recall</th><th>Avg Latency</th><th>False Positives</th></tr></thead>
          <tbody>
            {modalityPerf.map(m=>(
              <tr key={m.modality}>
                <td style={{fontWeight:600}}>{m.modality}</td>
                <td style={{color:m.precision>85?'var(--status-success)':'var(--status-warning)'}}>{m.precision}%</td>
                <td>{m.recall}%</td>
                <td style={{fontFamily:'var(--font-mono)'}}>{m.latency}s</td>
                <td>{Math.round((100-m.precision)*0.3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
