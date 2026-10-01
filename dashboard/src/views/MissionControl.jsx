import React, { useState } from 'react';
import { Shield, Play, Pause, RotateCcw, CheckCircle2, XCircle, Clock, AlertTriangle, Square } from 'lucide-react';
import { useMissionStore } from '../stores/missionStore';
import { useUIStore } from '../stores/uiStore';
import { MISSION_STATES } from '../utils/constants';

const precheckItems = [
  { id: 'ros2', name: 'ROS 2 Topics', desc: 'All 24 topics publishing at expected rates' },
  { id: 'slam', name: 'SLAM Init', desc: 'RTAB-Map initialized, first keyframe captured' },
  { id: 'sensors', name: 'Sensor Calibration', desc: 'All sensors within tolerance' },
  { id: 'battery', name: 'Battery Level', desc: 'Battery at 92% (> 30% required)' },
  { id: 'mqtt', name: 'MQTT Broker', desc: 'Mosquitto reachable, latency 2ms' },
  { id: 'uwb', name: 'UWB Anchors', desc: '4/4 anchors responding' },
  { id: 'odom', name: 'Odometry', desc: 'Wheel encoders reporting plausible values' },
  { id: 'cameras', name: 'Camera Feeds', desc: 'RGB, Depth, Thermal streaming' },
  { id: 'gas', name: 'Gas Sensors', desc: 'MQ-135 baseline drifting — recalibrate recommended' },
  { id: 'nav2', name: 'Nav2 Stack', desc: 'Navigation ready, costmaps loaded' },
];

const parameterDefaults = [
  { name: 'frontier_w_distance', label: 'Distance Weight', value: 1.0, min: 0, max: 3, step: 0.1 },
  { name: 'frontier_w_size', label: 'Size Weight', value: 0.5, min: 0, max: 3, step: 0.1 },
  { name: 'frontier_w_hazard', label: 'Hazard Avoidance', value: 0.3, min: 0, max: 3, step: 0.1 },
  { name: 'thermal_threshold', label: 'Thermal Threshold (°C)', value: 32, min: 20, max: 50, step: 1 },
  { name: 'max_linear_speed', label: 'Max Speed (m/s)', value: 0.5, min: 0.1, max: 1.5, step: 0.05 },
  { name: 'costmap_inflation', label: 'Costmap Inflation (m)', value: 0.3, min: 0.1, max: 1.0, step: 0.05 },
];

// Valid FSM transitions
const FSM_TRANSITIONS = {
  'IDLE': 'PRECHECK',
  'PRECHECK': 'DEPLOYED',
  'DEPLOYED': 'EXPLORING',
  'EXPLORING': 'RETURN_TO_BASE',
  'HAZARD_RESPONSE': 'EXPLORING',
  'VICTIM_CONFIRMED': 'EXPLORING',
  'MANUAL_OVERRIDE': 'EXPLORING',
  'RETURN_TO_BASE': 'MISSION_COMPLETE',
  'MISSION_COMPLETE': 'IDLE',
};

export default function MissionControl() {
  const { missionState, missionEvents, setMissionState, addEvent } = useMissionStore();
  const addToast = useUIStore((s) => s.addToast);
  const [params, setParams] = useState(parameterDefaults);
  const [checkStatuses, setCheckStatuses] = useState(
    precheckItems.reduce((acc, item) => ({ ...acc, [item.id]: item.id === 'gas' ? 'warning' : 'pass' }), {})
  );
  const [checking, setChecking] = useState(false);

  const handleStartMission = () => {
    const next = FSM_TRANSITIONS[missionState];
    if (!next) {
      addToast(`No valid transition from ${missionState}`, 'warning');
      return;
    }
    const now = new Date().toLocaleTimeString('en-US', { hour12: false });
    setMissionState(next);
    addEvent({
      id: Date.now(), type: 'state_change', severity: 'success',
      title: `State: ${missionState} → ${next}`,
      time: now, description: `Mission transitioned to ${next}`,
    });
    addToast(`Mission state → ${next}`, 'success');
  };

  const handlePause = () => {
    if (missionState === 'EXPLORING') {
      setMissionState('MANUAL_OVERRIDE');
      const now = new Date().toLocaleTimeString('en-US', { hour12: false });
      addEvent({
        id: Date.now(), type: 'state_change', severity: 'warning',
        title: 'Manual Override Engaged', time: now,
        description: 'Autonomous exploration paused by operator',
      });
      addToast('Mission paused → MANUAL_OVERRIDE', 'warning');
    } else if (missionState === 'MANUAL_OVERRIDE') {
      setMissionState('EXPLORING');
      addToast('Resuming autonomous exploration', 'success');
      addEvent({
        id: Date.now(), type: 'state_change', severity: 'info',
        title: 'Exploration Resumed', time: new Date().toLocaleTimeString('en-US', { hour12: false }),
        description: 'Autonomous mode re-engaged',
      });
    } else {
      addToast(`Cannot pause in ${missionState} state`, 'warning');
    }
  };

  const handleReturnToBase = () => {
    if (['EXPLORING', 'MANUAL_OVERRIDE', 'HAZARD_RESPONSE', 'VICTIM_CONFIRMED'].includes(missionState)) {
      const now = new Date().toLocaleTimeString('en-US', { hour12: false });
      setMissionState('RETURN_TO_BASE');
      addEvent({
        id: Date.now(), type: 'state_change', severity: 'critical',
        title: 'Return to Base Commanded', time: now,
        description: 'Operator commanded RTB — robot navigating to base',
      });
      addToast('Robot returning to base', 'critical');
    } else {
      addToast(`Cannot RTB from ${missionState}`, 'warning');
    }
  };

  const handleRunChecks = () => {
    setChecking(true);
    const ids = precheckItems.map(i => i.id);
    // Reset all to pending
    setCheckStatuses(ids.reduce((a, id) => ({ ...a, [id]: 'pending' }), {}));

    // Progressively check each item
    ids.forEach((id, i) => {
      setTimeout(() => {
        setCheckStatuses(prev => ({
          ...prev,
          [id]: id === 'gas' ? 'warning' : 'pass',
        }));
        if (i === ids.length - 1) {
          setChecking(false);
          addToast('Pre-deployment checks complete — 9/10 passed', 'success');
        }
      }, (i + 1) * 400);
    });
  };

  const handleParamChange = (index, newValue) => {
    const updated = [...params];
    updated[index] = { ...params[index], value: newValue };
    setParams(updated);
    addToast(`${params[index].label} → ${newValue.toFixed(2)}`, 'info');
  };

  return (
    <div className="animate-in">
      {/* FSM State Diagram */}
      <div className="glass-card" style={{ marginBottom: 16 }}>
        <div className="card-title">Mission State Machine</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
          {MISSION_STATES.map((state, i) => (
            <React.Fragment key={state}>
              <div className={`fsm-node ${state === missionState ? 'active' : ''}`}
                style={{ cursor: 'pointer' }}
                onClick={() => {
                  setMissionState(state);
                  addToast(`Forced state → ${state}`, 'warning');
                  addEvent({ id: Date.now(), type: 'state_change', severity: 'warning',
                    title: `Force set: ${state}`, time: new Date().toLocaleTimeString('en-US', { hour12: false }),
                    description: `Operator force-set state to ${state}` });
                }}>
                {state}
              </div>
              {i < MISSION_STATES.length - 1 && <span className="fsm-arrow">→</span>}
            </React.Fragment>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
          <button className="btn btn-primary" onClick={handleStartMission}>
            <Play size={14} /> {missionState === 'IDLE' ? 'Start Mission' : 'Next State'}
          </button>
          <button className="btn btn-ghost" onClick={handlePause}>
            {missionState === 'MANUAL_OVERRIDE' ? <><Play size={14} /> Resume</> : <><Pause size={14} /> Pause</>}
          </button>
          <button className="btn btn-danger" onClick={handleReturnToBase}>
            <RotateCcw size={14} /> Return to Base
          </button>
        </div>
      </div>

      <div className="content-grid">
        {/* Preflight Checks */}
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div className="card-title" style={{ marginBottom: 0 }}>Pre-Deployment Checks</div>
            <button className="btn btn-ghost" style={{ fontSize: '0.7rem', padding: '4px 10px' }}
              onClick={handleRunChecks} disabled={checking}>
              {checking ? 'Running…' : 'Re-run Checks'}
            </button>
          </div>
          {precheckItems.map((item) => (
            <div key={item.id} className="precheck-item">
              <div className={`precheck-indicator ${checkStatuses[item.id]}`}>
                {checkStatuses[item.id] === 'pass' ? <CheckCircle2 size={14} /> :
                 checkStatuses[item.id] === 'fail' ? <XCircle size={14} /> :
                 checkStatuses[item.id] === 'pending' ? <Clock size={14} /> :
                 <AlertTriangle size={14} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{item.name}</div>
                <div style={{ fontSize: '0.7rem', color: checkStatuses[item.id] === 'warning' ? 'var(--status-warning)' : checkStatuses[item.id] === 'pending' ? 'var(--text-muted)' : 'var(--status-success)' }}>
                  {checkStatuses[item.id] === 'pending' ? 'Checking…' : item.desc}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Mission Timeline */}
        <div className="glass-card">
          <div className="card-title">Mission Timeline ({missionEvents.length} events)</div>
          <div className="timeline" style={{ maxHeight: 450, overflowY: 'auto' }}>
            {missionEvents.map((event) => (
              <div key={event.id} className={`timeline-event ${event.severity}`}>
                <div className="timeline-time">{event.time}</div>
                <div className="timeline-title">{event.title}</div>
                <div className="timeline-desc">{event.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Parameter Tuning */}
      <div className="glass-card" style={{ marginTop: 16 }}>
        <div className="card-title">Real-Time Parameter Tuning</div>
        {params.map((p, i) => (
          <div key={p.name} className="param-row">
            <span className="param-label">{p.label}</span>
            <input
              type="range" className="param-slider"
              min={p.min} max={p.max} step={p.step}
              value={p.value}
              onChange={(e) => handleParamChange(i, parseFloat(e.target.value))}
            />
            <span className="param-value">{p.value.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
