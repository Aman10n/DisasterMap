export const MISSION_STATES = [
  'IDLE', 'PRECHECK', 'DEPLOYED', 'EXPLORING',
  'HAZARD_RESPONSE', 'VICTIM_CONFIRMED', 'MANUAL_OVERRIDE',
  'RETURN_TO_BASE', 'MISSION_COMPLETE'
];

export const HAZARD_TYPES = {
  gas_co: { label: 'Carbon Monoxide', unit: 'ppm', color: '#fbbf24' },
  gas_methane: { label: 'Methane', unit: 'ppm', color: '#f97316' },
  gas_nh3: { label: 'Ammonia', unit: 'ppm', color: '#a855f7' },
  gas_co2: { label: 'CO₂', unit: 'ppm', color: '#3b82f6' },
  fire_active: { label: 'Active Fire', unit: '°C', color: '#ef4444' },
  fire_hot_debris: { label: 'Hot Debris', unit: '°C', color: '#f97316' },
  structural_vibration: { label: 'Structural Vibration', unit: 'g', color: '#a855f7' },
  smoke: { label: 'Smoke/Low Visibility', unit: '%', color: '#64748b' },
};

export const DETECTION_MODALITIES = {
  thermal: { label: 'Thermal', icon: '🌡️', color: '#ef4444' },
  acoustic: { label: 'Acoustic', icon: '🔊', color: '#3b82f6' },
  co2: { label: 'CO₂', icon: '💨', color: '#10b981' },
  visual: { label: 'Visual', icon: '👁️', color: '#f59e0b' },
};

export const SENSOR_THRESHOLDS = {
  co_ppm: { warning: 25, critical: 50, unit: 'ppm' },
  methane_ppm: { warning: 5, critical: 10, unit: '% LEL' },
  nh3_ppm: { warning: 15, critical: 25, unit: 'ppm' },
  co2_ppm: { warning: 1000, critical: 5000, unit: 'ppm' },
};

const defaultWsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const defaultWsHost = window.location.port === '5173' ? 'localhost:8000' : window.location.host;
export const WS_URL = import.meta.env.VITE_WS_URL || `${defaultWsProtocol}//${defaultWsHost}/ws/live`;
