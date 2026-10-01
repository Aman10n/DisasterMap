import { create } from 'zustand';

export const useFleetStore = create((set) => ({
  robots: [
    {
      id: 'robot1', name: 'Explorer Alpha', isOnline: true, mode: 'exploring',
      x: 3.2, y: 5.1, z: 0, yaw: 1.2, battery: 78, speed: 0.35,
      coverage: 89.3, loopClosures: 12, slamQuality: 0.95,
      radioQuality: 0.88, cpuTemp: 62, gpuTemp: 58, ramUsage: 67,
    },
    {
      id: 'robot2', name: 'Scout Bravo', isOnline: true, mode: 'idle',
      x: -2.0, y: 1.5, z: 0, yaw: 0.5, battery: 92, speed: 0,
      coverage: 38.1, loopClosures: 5, slamQuality: 0.98,
      radioQuality: 0.95, cpuTemp: 45, gpuTemp: 40, ramUsage: 42,
    },
  ],

  updateRobot: (robotId, data) => set((s) => ({
    robots: s.robots.map((r) => r.id === robotId ? { ...r, ...data } : r),
  })),
  addRobot: (robot) => set((s) => ({ robots: [...s.robots, robot] })),
}));
