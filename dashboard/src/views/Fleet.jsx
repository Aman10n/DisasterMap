import React from 'react';
import { useFleetStore } from '../stores/fleetStore';
import { useUIStore } from '../stores/uiStore';
import { Battery, Wifi, Cpu, Thermometer, Navigation } from 'lucide-react';

function RobotCard({ robot }) {
  const updateRobot = useFleetStore((s) => s.updateRobot);
  const addToast = useUIStore((s) => s.addToast);
  const batteryColor = robot.battery > 50 ? 'var(--status-success)' : robot.battery > 20 ? 'var(--status-warning)' : 'var(--status-danger)';

  const handleNavGoal = () => {
    const goalX = Math.round((Math.random() * 12 - 6) * 10) / 10;
    const goalY = Math.round((Math.random() * 12 - 6) * 10) / 10;
    updateRobot(robot.id, { mode: 'nav_goal', speed: 0.4 });
    addToast(`${robot.name}: Nav goal → (${goalX}, ${goalY})`, 'info');
    // Simulate arrival after 3s
    setTimeout(() => {
      updateRobot(robot.id, { mode: 'exploring', x: goalX, y: goalY });
      addToast(`${robot.name}: Reached goal (${goalX}, ${goalY}) ✓`, 'success');
    }, 3000);
  };

  const handleManual = () => {
    updateRobot(robot.id, { mode: robot.mode === 'manual' ? 'exploring' : 'manual', speed: 0 });
    addToast(`${robot.name}: ${robot.mode === 'manual' ? 'Auto mode' : 'Manual mode'}`, 'info');
  };

  const handleStop = () => {
    updateRobot(robot.id, { mode: 'stopped', speed: 0 });
    addToast(`${robot.name}: EMERGENCY STOP ⛔`, 'critical');
    // Auto-resume after 5s
    setTimeout(() => {
      updateRobot(robot.id, { mode: 'idle' });
    }, 5000);
  };

  return (
    <div className={`robot-card ${robot.isOnline ? '' : 'offline'}`}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: '1rem', fontWeight: 700 }}>{robot.name}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{robot.id}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className={`status-dot ${robot.isOnline ? 'online' : 'offline'}`} />
          <span style={{
            fontSize: '0.75rem', fontWeight: 600,
            color: robot.mode === 'stopped' ? 'var(--status-danger)' : robot.isOnline ? 'var(--status-success)' : 'var(--text-muted)',
          }}>
            {robot.isOnline ? robot.mode.toUpperCase() : 'OFFLINE'}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, fontSize: '0.8rem' }}>
        <div className="status-row"><span className="label"><Battery size={13} style={{ marginRight: 4 }} />Battery</span><span className="value" style={{ color: batteryColor }}>{robot.battery}%</span></div>
        <div className="status-row"><span className="label"><Navigation size={13} style={{ marginRight: 4 }} />Speed</span><span className="value">{robot.speed} m/s</span></div>
        <div className="status-row"><span className="label"><Wifi size={13} style={{ marginRight: 4 }} />Signal</span><span className="value">{(robot.radioQuality * 100).toFixed(0)}%</span></div>
        <div className="status-row"><span className="label"><Cpu size={13} style={{ marginRight: 4 }} />Coverage</span><span className="value" style={{ color: 'var(--accent-cyan)' }}>{robot.coverage} m²</span></div>
        <div className="status-row"><span className="label"><Thermometer size={13} style={{ marginRight: 4 }} />CPU</span><span className="value">{robot.cpuTemp}°C</span></div>
        <div className="status-row"><span className="label">SLAM</span><span className="value" style={{ color: robot.slamQuality > 0.9 ? 'var(--status-success)' : 'var(--status-warning)' }}>{(robot.slamQuality * 100).toFixed(0)}%</span></div>
      </div>

      <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
        <button className="btn btn-primary" style={{ flex: 1, fontSize: '0.7rem' }} onClick={handleNavGoal}
          disabled={robot.mode === 'stopped'}>Nav Goal</button>
        <button className="btn btn-ghost" style={{ flex: 1, fontSize: '0.7rem' }} onClick={handleManual}
          disabled={robot.mode === 'stopped'}>
          {robot.mode === 'manual' ? 'Auto' : 'Manual'}
        </button>
        <button className="btn btn-danger" style={{ fontSize: '0.7rem' }} onClick={handleStop}>Stop</button>
      </div>
    </div>
  );
}

export default function Fleet() {
  const robots = useFleetStore((s) => s.robots);
  const totalCoverage = robots.reduce((s, r) => s + r.coverage, 0);

  return (
    <div className="animate-in">
      <div className="stats-grid">
        <div className="glass-card"><div className="card-title">Active Robots</div><div className="card-value accent">{robots.filter(r => r.isOnline).length}<span style={{ fontSize: '1rem' }}>/{robots.length}</span></div></div>
        <div className="glass-card"><div className="card-title">Total Coverage</div><div className="card-value accent">{totalCoverage.toFixed(1)}<span style={{ fontSize: '0.8rem', marginLeft: 4, color: 'var(--text-muted)' }}>m²</span></div></div>
        <div className="glass-card"><div className="card-title">Loop Closures</div><div className="card-value">{robots.reduce((s, r) => s + r.loopClosures, 0)}</div></div>
        <div className="glass-card"><div className="card-title">Avg Battery</div><div className="card-value accent">{(robots.reduce((s, r) => s + r.battery, 0) / robots.length).toFixed(0)}%</div></div>
      </div>

      <div className="content-grid">
        {robots.map((robot) => <RobotCard key={robot.id} robot={robot} />)}
      </div>

      <div className="glass-card">
        <div className="card-title">Voronoi Frontier Assignments</div>
        <table className="data-table">
          <thead><tr><th>Robot</th><th>Mode</th><th>Position</th><th>Speed</th><th>Battery</th></tr></thead>
          <tbody>
            {robots.map(r => (
              <tr key={r.id}>
                <td style={{ color: r.id === 'robot1' ? 'var(--accent-cyan)' : 'var(--accent-blue)', fontWeight: 600 }}>{r.name}</td>
                <td style={{ color: r.mode === 'stopped' ? 'var(--status-danger)' : 'var(--text-primary)', fontWeight: 600 }}>{r.mode.toUpperCase()}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>({r.x}, {r.y})</td>
                <td>{r.speed} m/s</td>
                <td style={{ color: r.battery > 50 ? 'var(--status-success)' : 'var(--status-warning)' }}>{r.battery}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
