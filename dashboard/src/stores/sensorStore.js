import { create } from 'zustand';

export const useSensorStore = create((set) => ({
  // Current robot sensor readings
  sensorData: {
    co_ppm: 12.3,
    co2_ppm: 487,
    methane_ppm: 0.8,
    nh3_ppm: 2.1,
    temperature: 24.5,
    humidity: 52,
    visibility: 82,
    vibration: 0.04,
  },

  // IoT deployed nodes
  iotNodes: [
    { id: 'node_01', deployed: true, online: true, battery: 95, temp: 23.1, co: 3.2, vibration: 0.02, motion: false, x: 2.1, y: 4.5 },
    { id: 'node_02', deployed: true, online: true, battery: 88, temp: 25.7, co: 8.9, vibration: 0.15, motion: false, x: -1.3, y: 8.2 },
    { id: 'node_03', deployed: true, online: false, battery: 72, temp: null, co: null, vibration: null, motion: false, x: 6.0, y: 2.1 },
    { id: 'node_04', deployed: false, online: false, battery: 100, temp: null, co: null, vibration: null, motion: false, x: null, y: null },
    { id: 'node_05', deployed: false, online: false, battery: 100, temp: null, co: null, vibration: null, motion: false, x: null, y: null },
  ],

  // Time series for charts
  sensorHistory: {
    co_ppm: Array.from({ length: 60 }, (_, i) => ({ time: i, value: 5 + Math.random() * 15 })),
    co2_ppm: Array.from({ length: 60 }, (_, i) => ({ time: i, value: 420 + Math.random() * 80 })),
    temperature: Array.from({ length: 60 }, (_, i) => ({ time: i, value: 22 + Math.random() * 5 })),
  },

  updateSensor: (key, value) => set((s) => ({
    sensorData: { ...s.sensorData, [key]: value },
  })),
  updateNode: (nodeId, data) => set((s) => ({
    iotNodes: s.iotNodes.map((n) => n.id === nodeId ? { ...n, ...data } : n),
  })),
}));
