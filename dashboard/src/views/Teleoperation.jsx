import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Camera, Hand, StopCircle, Navigation } from 'lucide-react';
import { useFleetStore } from '../stores/fleetStore';
import { useUIStore } from '../stores/uiStore';

function JoystickControl({ onMove }) {
  const canvasRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [handlePos, setHandlePos] = useState({ x: 100, y: 100 });
  const center = { x: 100, y: 100 };
  const maxR = 70;

  useEffect(() => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext('2d');
    ctx.clearRect(0, 0, 200, 200);
    ctx.beginPath(); ctx.arc(100,100,90,0,Math.PI*2); ctx.strokeStyle='rgba(148,163,184,0.15)'; ctx.lineWidth=1; ctx.stroke();
    ctx.beginPath(); ctx.arc(100,100,60,0,Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(100,20); ctx.lineTo(100,180); ctx.moveTo(20,100); ctx.lineTo(180,100);
    ctx.strokeStyle='rgba(148,163,184,0.08)'; ctx.stroke();
    const g = ctx.createRadialGradient(handlePos.x,handlePos.y,0,handlePos.x,handlePos.y,25);
    g.addColorStop(0,'#06d6a0'); g.addColorStop(1,'#118ab2');
    ctx.beginPath(); ctx.arc(handlePos.x,handlePos.y,25,0,Math.PI*2); ctx.fillStyle=g; ctx.shadowColor='#06d6a0'; ctx.shadowBlur=15; ctx.fill(); ctx.shadowBlur=0;
  }, [handlePos]);

  const onMouseMove = useCallback((e) => {
    if (!dragging) return;
    const r = canvasRef.current.getBoundingClientRect();
    let x=e.clientX-r.left, y=e.clientY-r.top;
    const dx=x-center.x, dy=y-center.y, d=Math.sqrt(dx*dx+dy*dy);
    if(d>maxR){x=center.x+(dx/d)*maxR; y=center.y+(dy/d)*maxR;}
    setHandlePos({x,y});
    const lx = -(y-center.y)/maxR*0.5;
    const az = -(x-center.x)/maxR;
    onMove?.(lx, 0, az);
  }, [dragging, onMove]);

  const reset = () => { setDragging(false); setHandlePos(center); onMove?.(0,0,0); };

  return (
    <canvas ref={canvasRef} width={200} height={200} className="joystick-container"
      onMouseDown={()=>setDragging(true)} onMouseUp={reset} onMouseLeave={reset} onMouseMove={onMouseMove} />
  );
}

function VideoFeed({ label, thermal }) {
  return (
    <div className="video-feed" style={{
      display:'flex',alignItems:'center',justifyContent:'center',
      background: thermal ? 'linear-gradient(135deg,#1a1a2e,#2d0a3e,#4a0e0e,#8b2500)' : 'linear-gradient(135deg,#111827,#1a2035)',
    }}>
      <div className="feed-label">{label}</div>
      <div style={{color:'var(--text-muted)',fontSize:'0.8rem',textAlign:'center'}}>
        <Camera size={24} style={{display:'block',margin:'0 auto 8px'}}/>{label} Feed
      </div>
    </div>
  );
}

export default function Teleoperation() {
  const [cmdVel, setCmdVel] = useState({ lx:0, az:0 });
  const [deadMan, setDeadMan] = useState(false);
  const [armAngles, setArmAngles] = useState([0, 0, 0, 0, 0, 0]);
  const [stopped, setStopped] = useState(false);
  const updateRobot = useFleetStore((s) => s.updateRobot);
  const addToast = useUIStore((s) => s.addToast);
  const joints = ['Base', 'Shoulder', 'Elbow', 'Wrist Pitch', 'Wrist Roll', 'Gripper'];

  const handleMove = (lx, ly, az) => {
    if (stopped) return;
    setCmdVel({ lx, az });
    if (deadMan) {
      updateRobot('robot1', { speed: Math.abs(lx).toFixed(2) });
    }
  };

  const handleDeadManDown = () => {
    setDeadMan(true);
    addToast('Dead-man switch ENGAGED — joystick active', 'info');
  };

  const handleDeadManUp = () => {
    setDeadMan(false);
    setCmdVel({ lx: 0, az: 0 });
    updateRobot('robot1', { speed: 0 });
  };

  const handleEmergencyStop = () => {
    setStopped(true);
    setCmdVel({ lx: 0, az: 0 });
    setDeadMan(false);
    updateRobot('robot1', { mode: 'stopped', speed: 0 });
    addToast('EMERGENCY STOP ACTIVATED ⛔', 'critical');
    setTimeout(() => {
      setStopped(false);
      updateRobot('robot1', { mode: 'manual' });
      addToast('E-Stop released — controls unlocked', 'info');
    }, 5000);
  };

  const handleArmChange = (index, value) => {
    const updated = [...armAngles];
    updated[index] = value;
    setArmAngles(updated);
  };

  return (
    <div className="animate-in">
      {stopped && (
        <div className="alert-banner critical">
          <StopCircle size={18} />
          <strong>EMERGENCY STOP ACTIVE</strong> — Controls locked for 5 seconds
        </div>
      )}
      <div className="content-grid">
        <div>
          <div className="glass-card" style={{marginBottom:16}}>
            <div className="card-title">Manual Control {stopped ? '(LOCKED)' : ''}</div>
            <div style={{display:'flex',gap:24,alignItems:'flex-start'}}>
              <JoystickControl onMove={handleMove}/>
              <div style={{flex:1}}>
                <div style={{fontSize:'0.8rem',marginBottom:8}}>
                  <span style={{color:'var(--text-muted)'}}>Linear: </span>
                  <span style={{fontFamily:'var(--font-mono)',color: stopped ? 'var(--status-danger)' : 'var(--accent-cyan)'}}>{cmdVel.lx.toFixed(2)} m/s</span>
                </div>
                <div style={{fontSize:'0.8rem',marginBottom:16}}>
                  <span style={{color:'var(--text-muted)'}}>Angular: </span>
                  <span style={{fontFamily:'var(--font-mono)',color: stopped ? 'var(--status-danger)' : 'var(--accent-cyan)'}}>{cmdVel.az.toFixed(2)} rad/s</span>
                </div>
                <button className="btn btn-primary" disabled={stopped}
                  style={{width:'100%',marginBottom:8,padding:'12px 16px',
                    background: deadMan ? 'linear-gradient(135deg, #f59e0b, #ef4444)' : undefined}}
                  onMouseDown={handleDeadManDown} onMouseUp={handleDeadManUp} onMouseLeave={handleDeadManUp}>
                  <Hand size={16}/> {deadMan ? '🔴 ACTIVE — Release to Stop' : 'Hold Dead-Man Switch'}
                </button>
                <button className="btn btn-danger" style={{width:'100%',padding:'12px 16px'}} onClick={handleEmergencyStop} disabled={stopped}>
                  <StopCircle size={16}/> Emergency Stop
                </button>
              </div>
            </div>
          </div>
          <div className="glass-card">
            <div className="card-title">Arm Control (6-DOF)</div>
            {joints.map((j,i)=>(
              <div key={i} className="param-row">
                <span className="param-label" style={{minWidth:110,fontSize:'0.75rem'}}>{j}</span>
                <input type="range" className="param-slider" min={-180} max={180}
                  value={armAngles[i]}
                  onChange={(e) => handleArmChange(i, parseInt(e.target.value))}/>
                <span className="param-value" style={{minWidth:40}}>{armAngles[i]}°</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="glass-card" style={{marginBottom:16}}>
            <div className="card-title">Camera Feeds</div>
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
              <VideoFeed label="RGB"/><VideoFeed label="Thermal" thermal/>
              <VideoFeed label="Depth"/><VideoFeed label="Wide Angle"/>
            </div>
          </div>
          <div className="glass-card">
            <div className="card-title">Click-to-Go Navigation</div>
            <div style={{height:120,background:'var(--bg-tertiary)',borderRadius:'var(--radius-md)',display:'flex',alignItems:'center',justifyContent:'center',color:'var(--text-muted)',fontSize:'0.8rem',cursor:'crosshair'}}
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const nx = ((e.clientX - rect.left) / rect.width * 16 - 8).toFixed(1);
                const ny = ((e.clientY - rect.top) / rect.height * 16 - 8).toFixed(1);
                addToast(`Nav goal sent → (${nx}, ${ny})`, 'success');
              }}>
              <Navigation size={16} style={{marginRight:6}}/> Click any point to set nav goal
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
