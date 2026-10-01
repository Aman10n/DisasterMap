import React, { useState } from 'react';
import { Users, Eye, X, ThermometerSun } from 'lucide-react';
import { DETECTION_MODALITIES } from '../utils/constants';
import { useUIStore } from '../stores/uiStore';

const initialVictims = [
  { id: 1, x: 2.5, y: -3.2, z: 0.1, floor: 0, confidence: 0.94,
    modalities: ['thermal', 'acoustic', 'visual'], status: 'confirmed',
    confirmedAt: '14:41:30', burialDepth: 'partial',
    bodyVisible: ['head', 'shoulders', 'left arm'],
    thermalTemp: 36.8, acousticHz: 340, co2Delta: 45 },
  { id: 2, x: -4.1, y: 5.8, z: 0.0, floor: 0, confidence: 0.87,
    modalities: ['thermal', 'co2', 'acoustic'], status: 'confirmed',
    confirmedAt: '14:52:15', burialDepth: 'deep', bodyVisible: [],
    thermalTemp: 34.2, acousticHz: 580, co2Delta: 120 },
  { id: 3, x: 6.2, y: -1.4, z: 0.0, floor: 0, confidence: 0.72,
    modalities: ['thermal', 'visual'], status: 'hypothesis',
    confirmedAt: null, burialDepth: 'surface', bodyVisible: ['full body'],
    thermalTemp: 35.1, acousticHz: null, co2Delta: null },
];

function ModalityBadge({ modality }) {
  const info = DETECTION_MODALITIES[modality];
  if (!info) return null;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      padding: '2px 8px', borderRadius: 12, fontSize: '0.7rem', fontWeight: 600,
      background: `${info.color}20`, color: info.color, border: `1px solid ${info.color}40`,
    }}>
      {info.icon} {info.label}
    </span>
  );
}

function EvidenceModal({ victim, onClose }) {
  if (!victim) return null;
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 10000,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      backdropFilter: 'blur(8px)', animation: 'fade-in 0.2s',
    }} onClick={onClose}>
      <div className="glass-card" style={{
        width: 600, maxHeight: '80vh', overflow: 'auto', padding: 24,
        border: '1px solid rgba(249,115,22,0.4)',
      }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div className="victim-id" style={{ fontSize: '1rem' }}>Evidence — Victim #{victim.id}</div>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: 4 }}><X size={18} /></button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
          {/* Thermal evidence */}
          <div style={{ background: 'linear-gradient(135deg,#1a1a2e,#4a0e0e,#8b2500)', borderRadius: 'var(--radius-md)', padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 600, marginBottom: 8, color: '#ef4444' }}>THERMAL IMAGE</div>
            <ThermometerSun size={32} style={{ color: '#ef4444', marginBottom: 8 }} />
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.5rem', color: '#ef4444' }}>{victim.thermalTemp}°C</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Above ambient: +{(victim.thermalTemp - 22).toFixed(1)}°C</div>
          </div>
          {/* Acoustic evidence */}
          <div style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 600, marginBottom: 8, color: '#3b82f6' }}>ACOUSTIC SIGNAL</div>
            <div style={{ fontSize: '2rem', marginBottom: 4 }}>🔊</div>
            {victim.acousticHz ? (
              <>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', color: '#3b82f6' }}>{victim.acousticHz} Hz</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Human voice range detected</div>
              </>
            ) : (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No acoustic data</div>
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
          {/* CO2 evidence */}
          <div style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 600, marginBottom: 8, color: '#10b981' }}>CO₂ TRACE</div>
            <div style={{ fontSize: '2rem', marginBottom: 4 }}>💨</div>
            {victim.co2Delta ? (
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', color: '#10b981' }}>+{victim.co2Delta} ppm</div>
            ) : (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No CO₂ trace</div>
            )}
          </div>
          {/* Visual */}
          <div style={{ background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', padding: 16, textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 600, marginBottom: 8, color: '#f59e0b' }}>VISUAL DETECTION</div>
            <div style={{ fontSize: '2rem', marginBottom: 4 }}>👁️</div>
            {victim.bodyVisible.length > 0 ? (
              <div style={{ fontSize: '0.8rem', color: '#f59e0b' }}>{victim.bodyVisible.join(', ')}</div>
            ) : (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Not visible (buried)</div>
            )}
          </div>
        </div>

        <div style={{ fontSize: '0.8rem', padding: 12, background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
          <div><strong>Position:</strong> ({victim.x}, {victim.y}, {victim.z}) — Floor {victim.floor}</div>
          <div><strong>Burial:</strong> {victim.burialDepth} — <strong>Confidence:</strong> {(victim.confidence * 100).toFixed(0)}%</div>
          <div><strong>Modalities:</strong> {victim.modalities.join(', ')}</div>
        </div>
      </div>
    </div>
  );
}

function VictimCard({ victim, onViewEvidence, onMarkRescued }) {
  const isConfirmed = victim.status === 'confirmed';
  const isRescued = victim.status === 'rescued';
  return (
    <div className="victim-card" style={{ opacity: isRescued ? 0.6 : 1 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
        <div>
          <div className="victim-id">Victim #{victim.id}</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: 2 }}>
            {isRescued ? '🟢 RESCUED' : isConfirmed ? '✅ CONFIRMED' : '⏳ HYPOTHESIS'}
          </div>
        </div>
        <div style={{
          padding: '4px 10px', borderRadius: 'var(--radius-xl)', fontSize: '0.75rem', fontWeight: 700,
          fontFamily: 'var(--font-mono)',
          background: isRescued ? 'rgba(16,185,129,0.25)' : isConfirmed ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
          color: isRescued ? 'var(--status-success)' : isConfirmed ? 'var(--status-success)' : 'var(--status-warning)',
          border: `1px solid ${isRescued ? 'rgba(16,185,129,0.5)' : isConfirmed ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'}`,
        }}>
          {(victim.confidence * 100).toFixed(0)}%
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, fontSize: '0.8rem', marginBottom: 10 }}>
        <div><span style={{ color: 'var(--text-muted)' }}>Position: </span><span style={{ fontFamily: 'var(--font-mono)' }}>({victim.x}, {victim.y})</span></div>
        <div><span style={{ color: 'var(--text-muted)' }}>Burial: </span><span style={{ textTransform: 'capitalize', color: victim.burialDepth === 'deep' ? 'var(--status-danger)' : 'var(--text-primary)' }}>{victim.burialDepth}</span></div>
      </div>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
        {victim.modalities.map((m) => <ModalityBadge key={m} modality={m} />)}
      </div>

      {victim.bodyVisible.length > 0 && (
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          <Eye size={12} style={{ marginRight: 4 }} />Visible: {victim.bodyVisible.join(', ')}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <button className="btn btn-primary" style={{ flex: 1, fontSize: '0.7rem' }} onClick={() => onViewEvidence(victim)}>View Evidence</button>
        {isConfirmed && !isRescued && (
          <button className="btn btn-ghost" style={{ fontSize: '0.7rem' }} onClick={() => onMarkRescued(victim.id)}>Mark Rescued</button>
        )}
        {isRescued && <span style={{ fontSize: '0.7rem', color: 'var(--status-success)', fontWeight: 600, padding: '8px 0' }}>✓ Rescued</span>}
      </div>
    </div>
  );
}

export default function Victims() {
  const [victims, setVictims] = useState(initialVictims);
  const [evidenceVictim, setEvidenceVictim] = useState(null);
  const addToast = useUIStore((s) => s.addToast);

  const confirmed = victims.filter(v => v.status === 'confirmed');
  const hypotheses = victims.filter(v => v.status === 'hypothesis');
  const rescued = victims.filter(v => v.status === 'rescued');

  const handleMarkRescued = (victimId) => {
    setVictims(prev => prev.map(v =>
      v.id === victimId ? { ...v, status: 'rescued' } : v
    ));
    addToast(`Victim #${victimId} marked as RESCUED ✓`, 'success');
  };

  return (
    <div className="animate-in">
      {evidenceVictim && <EvidenceModal victim={evidenceVictim} onClose={() => setEvidenceVictim(null)} />}

      {confirmed.length > 0 && (
        <div className="alert-banner critical">
          <Users size={18} />
          <strong>{confirmed.length} survivors confirmed</strong> — Rescue teams dispatched to coordinates
        </div>
      )}
      {rescued.length > 0 && (
        <div className="alert-banner success">
          <Users size={18} />
          <strong>{rescued.length} survivors rescued</strong> successfully
        </div>
      )}

      <div className="stats-grid">
        <div className="glass-card"><div className="card-title">Confirmed Survivors</div><div className="card-value warning">{confirmed.length}</div></div>
        <div className="glass-card"><div className="card-title">Active Hypotheses</div><div className="card-value">{hypotheses.length}</div></div>
        <div className="glass-card"><div className="card-title">Rescued</div><div className="card-value accent">{rescued.length}</div></div>
        <div className="glass-card"><div className="card-title">Avg. Confidence</div>
          <div className="card-value accent">{(victims.reduce((s,v)=>s+v.confidence,0)/victims.length*100).toFixed(0)}%</div>
        </div>
      </div>

      <div className="content-grid">
        {victims.map((victim) => (
          <VictimCard key={victim.id} victim={victim}
            onViewEvidence={setEvidenceVictim}
            onMarkRescued={handleMarkRescued} />
        ))}
      </div>
    </div>
  );
}
