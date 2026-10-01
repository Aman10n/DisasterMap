import React from 'react';
import { Radio, Battery, Thermometer, Wind, Activity } from 'lucide-react';
import { useSensorStore } from '../stores/sensorStore';
import { useFleetStore } from '../stores/fleetStore';
import { useUIStore } from '../stores/uiStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function NodeCard({ node }) {
  const updateNode = useSensorStore((s) => s.updateNode);
  const robots = useFleetStore((s) => s.robots);
  const addToast = useUIStore((s) => s.addToast);
  const statusColor = node.online ? 'var(--status-success)' : node.deployed ? 'var(--status-danger)' : 'var(--text-muted)';
  const statusLabel = node.online ? 'ONLINE' : node.deployed ? 'OFFLINE' : 'NOT DEPLOYED';

  const handleDeploy = () => {
    const robot = robots[0]; // Deploy at robot 1's position
    addToast(`Deploying ${node.id} at (${robot.x}, ${robot.y})…`, 'info');
    // Simulate deployment delay
    setTimeout(() => {
      updateNode(node.id, {
        deployed: true, online: true, x: robot.x, y: robot.y,
        temp: Math.round((22 + Math.random() * 5) * 10) / 10,
        co: Math.round(Math.random() * 15 * 10) / 10,
        vibration: Math.round(Math.random() * 0.1 * 100) / 100,
        motion: false,
      });
      addToast(`${node.id} deployed and ONLINE ✓`, 'success');
    }, 1500);
  };

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 700 }}>{node.id}</div>
          <div style={{ fontSize: '0.7rem', color: statusColor, fontWeight: 600 }}>
            <span className={`status-dot ${node.online ? 'online' : 'offline'}`} />{statusLabel}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Battery size={14} style={{ color: node.battery > 50 ? 'var(--status-success)' : 'var(--status-warning)' }} />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 600 }}>{node.battery}%</span>
        </div>
      </div>

      {node.deployed && node.online ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: '0.8rem' }}>
          <div className="status-row"><span className="label"><Thermometer size={12} /> Temp</span><span className="value">{node.temp}°C</span></div>
          <div className="status-row"><span className="label"><Wind size={12} /> CO</span><span className="value" style={{ color: node.co > 25 ? 'var(--status-danger)' : 'var(--text-primary)' }}>{node.co} ppm</span></div>
          <div className="status-row"><span className="label"><Activity size={12} /> Vibration</span><span className="value" style={{ color: node.vibration > 0.15 ? 'var(--status-warning)' : 'var(--text-primary)' }}>{node.vibration}g</span></div>
          <div className="status-row"><span className="label">Motion</span><span className="value">{node.motion ? '⚠️ YES' : 'No'}</span></div>
          <div className="status-row" style={{ gridColumn: '1/3' }}><span className="label">Position</span><span className="value" style={{ fontFamily: 'var(--font-mono)' }}>({node.x}, {node.y})</span></div>
        </div>
      ) : !node.deployed ? (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <button className="btn btn-primary" onClick={handleDeploy}>Deploy Node</button>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 8 }}>Click to deploy at robot's current position</div>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 16, color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          Connection lost. Last seen: 2 min ago
        </div>
      )}
    </div>
  );
}

export default function Sensors() {
  const { iotNodes, sensorHistory } = useSensorStore();
  const deployed = iotNodes.filter(n => n.deployed);
  const online = iotNodes.filter(n => n.online);

  return (
    <div className="animate-in">
      <div className="stats-grid">
        <div className="glass-card"><div className="card-title">Deployed Nodes</div><div className="card-value accent">{deployed.length}<span style={{ fontSize: '1rem' }}>/{iotNodes.length}</span></div></div>
        <div className="glass-card"><div className="card-title">Online</div><div className="card-value accent">{online.length}</div></div>
        <div className="glass-card"><div className="card-title">Avg Battery</div><div className="card-value">{(deployed.reduce((s,n)=>s+n.battery,0)/Math.max(deployed.length,1)).toFixed(0)}%</div></div>
        <div className="glass-card"><div className="card-title">Mesh Hops</div><div className="card-value accent">{Math.min(deployed.length, 3)}</div></div>
      </div>

      <div className="content-grid-3">
        {iotNodes.map((node) => <NodeCard key={node.id} node={node} />)}
      </div>

      <div className="glass-card" style={{ marginTop: 16 }}>
        <div className="card-title">Network Temperature Readings (Live)</div>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={sensorHistory.temperature}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} />
            <YAxis stroke="var(--text-muted)" fontSize={10} domain={['auto', 'auto']} />
            <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--glass-border)', borderRadius: 8 }} />
            <Line type="monotone" dataKey="value" stroke="var(--accent-cyan)" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
