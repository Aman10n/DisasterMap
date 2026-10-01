import { useEffect, useRef } from 'react';
import { useSensorStore } from '../stores/sensorStore';
import { useFleetStore } from '../stores/fleetStore';
import { useMissionStore } from '../stores/missionStore';

export function useSimulation() {
  const tickRef = useRef(0);

  useEffect(() => {
    const interval = setInterval(() => {
      tickRef.current += 1;
      const t = tickRef.current;

      // Update sensor readings every tick
      const { updateSensor } = useSensorStore.getState();
      updateSensor('co_ppm', Math.round((5 + 10 * Math.sin(t * 0.3) + (Math.random() - 0.5) * 4) * 10) / 10);
      updateSensor('co2_ppm', Math.round(420 + 50 * Math.sin(t * 0.2) + (Math.random() - 0.5) * 20));
      updateSensor('temperature', Math.round((22 + 3 * Math.sin(t * 0.1) + (Math.random() - 0.5)) * 10) / 10);
      updateSensor('humidity', Math.round(45 + 10 * Math.sin(t * 0.05)));
      updateSensor('visibility', Math.round(Math.max(20, Math.min(100, 85 - 15 * Math.sin(t * 0.08)))));

      // Update robot positions every tick
      const { updateRobot } = useFleetStore.getState();
      const r1x = 5 * Math.cos(t * 0.05) + (Math.random() - 0.5) * 0.1;
      const r1y = 5 * Math.sin(t * 0.07) + (Math.random() - 0.5) * 0.1;
      updateRobot('robot1', {
        x: Math.round(r1x * 100) / 100,
        y: Math.round(r1y * 100) / 100,
        yaw: Math.atan2(Math.cos(t * 0.07), -Math.sin(t * 0.05)),
        battery: Math.max(10, Math.round(78 - t * 0.05)),
        speed: Math.round((0.3 + 0.1 * Math.sin(t * 0.2)) * 100) / 100,
        cpuTemp: Math.round(60 + 5 * Math.sin(t * 0.1)),
      });

      // Update mission area explored
      const { missionState, updateStats } = useMissionStore.getState();
      if (missionState === 'EXPLORING') {
        updateStats({ areaExplored: Math.round((127.4 + t * 0.08) * 10) / 10 });
        updateStats({ explorationRate: Math.round((4.2 + Math.sin(t * 0.1) * 0.3) * 10) / 10 });
      }

      // Add sensor history points
      const store = useSensorStore.getState();
      const newCO = { time: t, value: store.sensorData.co_ppm };
      const newCO2 = { time: t, value: store.sensorData.co2_ppm };
      const newTemp = { time: t, value: store.sensorData.temperature };
      useSensorStore.setState({
        sensorHistory: {
          co_ppm: [...store.sensorHistory.co_ppm.slice(-59), newCO],
          co2_ppm: [...store.sensorHistory.co2_ppm.slice(-59), newCO2],
          temperature: [...store.sensorHistory.temperature.slice(-59), newTemp],
        },
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);
}
