import React, { useRef, useState, useMemo, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { useMissionStore } from '../stores/missionStore';
import { useSensorStore } from '../stores/sensorStore';
import { useFleetStore } from '../stores/fleetStore';
import { useUIStore } from '../stores/uiStore';
import * as THREE from 'three';

function EnvironmentVoxels() {
  const meshRef = useRef();
  const voxels = useMemo(() => {
    const positions = [];
    for (let x = -8; x < 8; x += 0.4) {
      for (let y = -8; y < 8; y += 0.4) {
        const isWall = (Math.abs(x) > 7) || (Math.abs(y) > 7) ||
          (Math.abs(x - 3) < 0.2 && y > -4 && y < 4) ||
          (Math.abs(y + 2) < 0.2 && x > -6 && x < 0);
        if (isWall) {
          for (let z = 0; z < 2.5; z += 0.4) { positions.push([x, z, y]); }
        }
        if (Math.random() < 0.15 && !isWall) { positions.push([x, Math.random() * 0.3, y]); }
      }
    }
    return positions;
  }, []);

  return (
    <instancedMesh ref={meshRef} args={[null, null, voxels.length]}>
      <boxGeometry args={[0.35, 0.35, 0.35]} />
      <meshStandardMaterial color="#1a8a6e" transparent opacity={0.7} />
      {voxels.map((pos, i) => {
        const matrix = new THREE.Matrix4();
        matrix.setPosition(...pos);
        if (meshRef.current) meshRef.current.setMatrixAt(i, matrix);
        return null;
      })}
    </instancedMesh>
  );
}

function RobotMarker({ position, color = '#06d6a0' }) {
  const ref = useRef();
  useFrame((_, delta) => { if (ref.current) ref.current.rotation.y += delta * 0.5; });
  return (
    <group position={[position[0], 0.3, position[1]]}>
      <mesh><boxGeometry args={[0.5, 0.3, 0.4]} /><meshStandardMaterial color={color} /></mesh>
      <mesh position={[0, 0.3, 0]} ref={ref}><octahedronGeometry args={[0.15]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} /></mesh>
      <pointLight color={color} intensity={2} distance={3} />
    </group>
  );
}

function VictimMarker3D({ position }) {
  const ref = useRef();
  useFrame((state) => { if (ref.current) ref.current.scale.setScalar(1 + 0.2 * Math.sin(state.clock.elapsedTime * 3)); });
  return (
    <group position={[position[0], 0.5, position[1]]}>
      <mesh ref={ref}><sphereGeometry args={[0.2, 16, 16]} /><meshStandardMaterial color="#f97316" emissive="#f97316" emissiveIntensity={0.8} transparent opacity={0.9} /></mesh>
      <pointLight color="#f97316" intensity={3} distance={5} />
    </group>
  );
}

function HazardZone3D({ position, radius, type }) {
  const color = type === 'gas' ? '#fbbf24' : type === 'fire' ? '#ef4444' : '#a855f7';
  return (
    <mesh position={[position[0], 0.1, position[1]]}>
      <cylinderGeometry args={[radius, radius, 0.1, 32]} />
      <meshStandardMaterial color={color} transparent opacity={0.25} />
    </mesh>
  );
}

function CameraReset({ trigger }) {
  const { camera } = useThree();
  React.useEffect(() => {
    if (trigger > 0) { camera.position.set(12, 10, 12); camera.lookAt(0, 0, 0); }
  }, [trigger, camera]);
  return null;
}

function Scene({ showGrid, resetTrigger }) {
  const robots = useFleetStore((s) => s.robots);
  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 15, 10]} intensity={0.8} />
      <pointLight position={[0, 8, 0]} intensity={0.5} color="#118ab2" />
      <EnvironmentVoxels />
      {robots.map((r) => (
        <RobotMarker key={r.id} position={[r.x, r.y]} color={r.id === 'robot1' ? '#06d6a0' : '#118ab2'} />
      ))}
      <VictimMarker3D position={[2.5, -3.2]} />
      <VictimMarker3D position={[-4.1, 5.8]} />
      <VictimMarker3D position={[6.2, -1.4]} />
      <HazardZone3D position={[5.8, -6.3]} radius={3} type="gas" />
      <HazardZone3D position={[-3.5, 7.0]} radius={2} type="fire" />
      {showGrid && <Grid infiniteGrid fadeDistance={30} cellSize={1} sectionSize={5} sectionColor="#118ab2" cellColor="#1a2035" />}
      <OrbitControls makeDefault maxPolarAngle={Math.PI / 2.1} minDistance={3} maxDistance={40} />
      <CameraReset trigger={resetTrigger} />
    </>
  );
}

function StatCard({ title, value, unit, accent }) {
  return (
    <div className="glass-card">
      <div className="card-title">{title}</div>
      <div className={`card-value ${accent || ''}`}>{value}<span style={{ fontSize: '0.9rem', marginLeft: 4, color: 'var(--text-muted)' }}>{unit}</span></div>
    </div>
  );
}

export default function LiveMap() {
  const { areaExplored, victimsConfirmed, hazardsDetected, explorationRate } = useMissionStore();
  const { sensorData } = useSensorStore();
  const addToast = useUIStore((s) => s.addToast);
  const [showGrid, setShowGrid] = useState(true);
  const [viewMode, setViewMode] = useState('3d');
  const [resetTrigger, setResetTrigger] = useState(0);

  const toggleGrid = () => {
    setShowGrid(p => !p);
    addToast(showGrid ? 'Grid hidden' : 'Grid visible', 'info');
  };

  const resetCamera = () => {
    setResetTrigger(p => p + 1);
    addToast('Camera reset to default', 'info');
  };

  const toggle2D = () => {
    setViewMode(p => p === '3d' ? '2d' : '3d');
    addToast(viewMode === '3d' ? 'Switched to 2D Floor Plan' : 'Switched to 3D View', 'info');
  };

  return (
    <div className="animate-in">
      <div className="stats-grid">
        <StatCard title="Area Explored" value={areaExplored.toFixed(1)} unit="m²" accent="accent" />
        <StatCard title="Survivors Found" value={victimsConfirmed} unit="" accent={victimsConfirmed > 0 ? 'warning' : ''} />
        <StatCard title="Active Hazards" value={hazardsDetected} unit="" accent={hazardsDetected > 0 ? 'danger' : ''} />
        <StatCard title="Exploration Rate" value={explorationRate.toFixed(1)} unit="m²/min" accent="accent" />
      </div>

      <div className="glass-card full-width" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="scene-container" style={{ height: 520 }}>
          {viewMode === '3d' ? (
            <Canvas camera={{ position: [12, 10, 12], fov: 50 }} gl={{ antialias: true, alpha: false }} style={{ background: '#0a0e1a' }}>
              <Scene showGrid={showGrid} resetTrigger={resetTrigger} />
            </Canvas>
          ) : (
            <div style={{ width: '100%', height: '100%', background: '#0a0e1a', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{ width: 400, height: 400, border: '1px solid var(--border-subtle)', position: 'relative', borderRadius: 'var(--radius-md)' }}>
                {/* 2D floor plan grid */}
                <svg width="100%" height="100%" viewBox="-10 -10 20 20">
                  <rect x="-8" y="-8" width="16" height="16" fill="none" stroke="#1a8a6e" strokeWidth="0.1" opacity="0.5" />
                  <line x1="-8" y1="0" x2="8" y2="0" stroke="#1a2035" strokeWidth="0.05" />
                  <line x1="0" y1="-8" x2="0" y2="8" stroke="#1a2035" strokeWidth="0.05" />
                  {/* Walls */}
                  <line x1="3" y1="-4" x2="3" y2="4" stroke="#1a8a6e" strokeWidth="0.15" />
                  <line x1="-6" y1="-2" x2="0" y2="-2" stroke="#1a8a6e" strokeWidth="0.15" />
                  {/* Robots */}
                  <circle cx={useFleetStore.getState().robots[0].x} cy={useFleetStore.getState().robots[0].y} r="0.4" fill="#06d6a0" />
                  <circle cx={useFleetStore.getState().robots[1].x} cy={useFleetStore.getState().robots[1].y} r="0.4" fill="#118ab2" />
                  {/* Victims */}
                  <circle cx="2.5" cy="-3.2" r="0.3" fill="#f97316" opacity="0.8" />
                  <circle cx="-4.1" cy="5.8" r="0.3" fill="#f97316" opacity="0.8" />
                  <circle cx="6.2" cy="-1.4" r="0.3" fill="#f97316" opacity="0.8" />
                  {/* Hazard zones */}
                  <circle cx="5.8" cy="-6.3" r="3" fill="#fbbf24" opacity="0.15" />
                  <circle cx="-3.5" cy="7.0" r="2" fill="#ef4444" opacity="0.15" />
                </svg>
                <div style={{ position: 'absolute', bottom: 8, left: 8, fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                  🟢 Robot &nbsp; 🟠 Victim &nbsp; 🟡 Gas &nbsp; 🔴 Fire
                </div>
              </div>
            </div>
          )}
          <div className="scene-overlay">
            <button className={`scene-overlay-btn ${viewMode === '2d' ? 'active' : ''}`}
              onClick={toggle2D} style={viewMode === '2d' ? { background: 'rgba(6,214,160,0.2)', color: 'var(--accent-cyan)' } : {}}>
              {viewMode === '3d' ? '2D Floor Plan' : '3D View'}
            </button>
            <button className="scene-overlay-btn" onClick={resetCamera}>Reset Camera</button>
            <button className="scene-overlay-btn" onClick={toggleGrid}
              style={!showGrid ? { background: 'rgba(239,68,68,0.15)', color: 'var(--status-danger)' } : {}}>
              {showGrid ? 'Hide Grid' : 'Show Grid'}
            </button>
          </div>
        </div>
      </div>

      <div className="stats-grid" style={{ marginTop: 16 }}>
        <div className="glass-card">
          <div className="card-title">CO Level</div>
          <div className={`card-value ${sensorData.co_ppm > 50 ? 'danger' : sensorData.co_ppm > 25 ? 'warning' : 'accent'}`}>
            {sensorData.co_ppm.toFixed(1)}<span style={{ fontSize: '0.8rem', marginLeft: 4, color: 'var(--text-muted)' }}>ppm</span>
          </div>
        </div>
        <div className="glass-card"><div className="card-title">CO₂</div><div className="card-value">{sensorData.co2_ppm}<span style={{ fontSize: '0.8rem', marginLeft: 4, color: 'var(--text-muted)' }}>ppm</span></div></div>
        <div className="glass-card"><div className="card-title">Temperature</div><div className="card-value accent">{sensorData.temperature}°C</div></div>
        <div className="glass-card">
          <div className="card-title">Visibility</div>
          <div className={`card-value ${sensorData.visibility < 40 ? 'danger' : 'accent'}`}>{sensorData.visibility}%</div>
        </div>
      </div>
    </div>
  );
}
