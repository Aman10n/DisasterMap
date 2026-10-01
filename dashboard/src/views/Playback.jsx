import React, { useState, useEffect, useRef } from 'react';
import { PlayCircle, Pause, SkipForward, SkipBack, Download, Clock } from 'lucide-react';
import { useUIStore } from '../stores/uiStore';

const demoMissions = [
  { id: 1, name: 'Earthquake Alpha', date: '2024-03-15', duration: '45:12', durationSec: 2712, area: 127.4, victims: 3 },
  { id: 2, name: 'Industrial Fire Bravo', date: '2024-03-10', duration: '32:08', durationSec: 1928, area: 89.2, victims: 1 },
  { id: 3, name: 'Tunnel Collapse Charlie', date: '2024-03-05', duration: '58:44', durationSec: 3524, area: 201.3, victims: 5 },
];

export default function Playback() {
  const [selected, setSelected] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [speed, setSpeed] = useState(1);
  const addToast = useUIStore((s) => s.addToast);
  const intervalRef = useRef(null);

  const selectedMission = demoMissions.find(m => m.id === selected);

  // Auto-advance progress when playing
  useEffect(() => {
    if (playing && selected) {
      intervalRef.current = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            setPlaying(false);
            addToast('Playback complete', 'success');
            return 100;
          }
          return Math.min(100, prev + (speed * 0.5));
        });
      }, 100);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [playing, selected, speed]);

  const handleSelectMission = (id) => {
    setSelected(id);
    setProgress(0);
    setPlaying(false);
    const m = demoMissions.find(mi => mi.id === id);
    addToast(`Loaded: ${m.name}`, 'info');
  };

  const handlePlayPause = () => {
    if (progress >= 100) { setProgress(0); }
    setPlaying(!playing);
    addToast(playing ? 'Playback paused' : `Playing at ${speed}× speed`, 'info');
  };

  const handleSkipBack = () => {
    setProgress(prev => Math.max(0, prev - 10));
    addToast('⏪ Skipped back', 'info');
  };

  const handleSkipForward = () => {
    setProgress(prev => Math.min(100, prev + 10));
    addToast('⏩ Skipped forward', 'info');
  };

  const handleSpeedChange = (s) => {
    setSpeed(s);
    addToast(`Playback speed: ${s}×`, 'info');
  };

  const handleDownload = () => {
    addToast('📄 Report generation started…', 'info');
    setTimeout(() => addToast('Report generated (PDF simulation)', 'success'), 2000);
  };

  const handleExport = () => {
    addToast('📦 Rosbag export queued', 'info');
    setTimeout(() => addToast('Rosbag exported successfully', 'success'), 2500);
  };

  const formatTime = (pct) => {
    if (!selectedMission) return '0:00';
    const sec = Math.floor(selectedMission.durationSec * pct / 100);
    return `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`;
  };

  return (
    <div className="animate-in">
      <div className="stats-grid">
        <div className="glass-card"><div className="card-title">Recorded Missions</div><div className="card-value accent">{demoMissions.length}</div></div>
        <div className="glass-card"><div className="card-title">Total Duration</div><div className="card-value">2h 16m</div></div>
        <div className="glass-card"><div className="card-title">Total Area Mapped</div><div className="card-value accent">417.9 m²</div></div>
        <div className="glass-card"><div className="card-title">Total Survivors</div><div className="card-value warning">9</div></div>
      </div>

      <div className="content-grid">
        <div className="glass-card">
          <div className="card-title">Mission Recordings</div>
          {demoMissions.map(m=>(
            <div key={m.id} onClick={()=>handleSelectMission(m.id)}
              style={{
                padding:'12px', borderRadius:'var(--radius-md)', marginBottom:8, cursor:'pointer',
                background: selected===m.id ? 'rgba(6,214,160,0.1)' : 'transparent',
                border: `1px solid ${selected===m.id ? 'var(--border-accent)' : 'var(--border-subtle)'}`,
                transition:'var(--transition-fast)',
              }}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                <div>
                  <div style={{fontWeight:600,fontSize:'0.9rem'}}>{m.name}</div>
                  <div style={{fontSize:'0.75rem',color:'var(--text-muted)'}}>
                    <Clock size={11} style={{marginRight:4}}/>{m.date} · {m.duration}
                  </div>
                </div>
                <div style={{textAlign:'right',fontSize:'0.8rem'}}>
                  <div style={{color:'var(--accent-cyan)'}}>{m.area} m²</div>
                  <div style={{color:'var(--victim-color)'}}>{m.victims} survivors</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="glass-card">
          <div className="card-title">Playback Controls</div>
          {selected ? (
            <>
              <div style={{height:220,background:'var(--bg-tertiary)',borderRadius:'var(--radius-md)',display:'flex',alignItems:'center',justifyContent:'center',color:'var(--text-muted)',marginBottom:16,position:'relative',overflow:'hidden'}}>
                <div style={{
                  position:'absolute',bottom:0,left:0,height:'100%',
                  width:`${progress}%`,background:'rgba(6,214,160,0.08)',
                  transition:'width 0.1s linear',
                }}/>
                <div style={{zIndex:1,textAlign:'center'}}>
                  <div style={{fontSize:'2rem',fontFamily:'var(--font-mono)',color:'var(--accent-cyan)'}}>{formatTime(progress)}</div>
                  <div style={{fontSize:'0.75rem',color:'var(--text-muted)',marginTop:4}}>
                    {playing ? `Playing at ${speed}×` : progress >= 100 ? 'Complete' : 'Paused'}
                  </div>
                  <div style={{fontSize:'0.75rem',color:'var(--text-secondary)',marginTop:2}}>
                    {selectedMission.name} — {Math.round(selectedMission.area * progress / 100)} m² mapped
                  </div>
                </div>
              </div>
              <div style={{marginBottom:12}}>
                <input type="range" className="param-slider" style={{width:'100%'}}
                  min={0} max={100} value={progress} step={0.5}
                  onChange={e=>setProgress(parseFloat(e.target.value))}/>
                <div style={{display:'flex',justifyContent:'space-between',fontSize:'0.7rem',color:'var(--text-muted)',marginTop:4}}>
                  <span>{formatTime(progress)}</span>
                  <span>{selectedMission.duration}</span>
                </div>
              </div>
              <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:12}}>
                <button className="btn btn-ghost" onClick={handleSkipBack}><SkipBack size={16}/></button>
                <button className="btn btn-primary" style={{padding:'10px 24px'}} onClick={handlePlayPause}>
                  {playing ? <Pause size={18}/> : <PlayCircle size={18}/>}
                </button>
                <button className="btn btn-ghost" onClick={handleSkipForward}><SkipForward size={16}/></button>
                <div style={{marginLeft:16,display:'flex',gap:4}}>
                  {[1,4,16].map(s=>(
                    <button key={s} className={`btn ${speed===s?'btn-primary':'btn-ghost'}`}
                      style={{fontSize:'0.7rem',padding:'4px 8px'}} onClick={()=>handleSpeedChange(s)}>
                      {s}×
                    </button>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div style={{textAlign:'center',padding:40,color:'var(--text-muted)'}}>
              Select a mission recording to begin playback
            </div>
          )}
          {selected && (
            <div style={{marginTop:16,display:'flex',gap:8}}>
              <button className="btn btn-primary" style={{flex:1}} onClick={handleDownload}><Download size={14}/> Download Report</button>
              <button className="btn btn-ghost" style={{flex:1}} onClick={handleExport}>Export Rosbag</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
