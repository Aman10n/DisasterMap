import { create } from 'zustand';

export const useMissionStore = create((set) => ({
  missionId: null,
  missionName: 'Earthquake Response Alpha',
  missionState: 'EXPLORING',
  areaExplored: 127.4,
  victimsConfirmed: 3,
  hazardsDetected: 5,
  explorationRate: 4.2,
  missionEvents: [
    { id: 1, type: 'state_change', severity: 'info', title: 'Mission Started', time: '14:32:05', description: 'Robot deployed to Zone A' },
    { id: 2, type: 'detection', severity: 'warning', title: 'Thermal Anomaly Detected', time: '14:35:12', description: '47.2°C hotspot at (3.2, 7.1)' },
    { id: 3, type: 'slam', severity: 'info', title: 'Loop Closure #4', time: '14:38:00', description: 'Drift corrected: 0.12m → 0.03m' },
    { id: 4, type: 'detection', severity: 'critical', title: 'VICTIM CONFIRMED', time: '14:41:30', description: 'Thermal + Acoustic + Visual — Confidence: 0.94' },
    { id: 5, type: 'hazard', severity: 'critical', title: 'CO Level: 62 ppm (IDLH)', time: '14:44:15', description: 'No-go zone injected at (5.8, 12.3)' },
  ],

  setMissionState: (state) => set({ missionState: state }),
  setMissionName: (name) => set({ missionName: name }),
  addEvent: (event) => set((s) => ({ missionEvents: [event, ...s.missionEvents] })),
  updateStats: (stats) => set(stats),
}));
