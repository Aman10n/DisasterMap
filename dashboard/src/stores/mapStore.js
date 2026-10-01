import { create } from 'zustand';

export const useMapStore = create((set) => ({
  meshData: null,
  robotTrail: [],
  annotations: [],
  victimMarkers: [],
  hazardVolumes: [],
  currentFloor: 0,
  floorLevels: [{ index: 0, label: 'Ground Floor', min: -0.3, max: 3.0 }],
  heightSlider: 1.5,

  setMeshData: (data) => set({ meshData: data }),
  addTrailPoint: (point) => set((s) => ({
    robotTrail: [...s.robotTrail.slice(-500), point],
  })),
  setAnnotations: (annotations) => set({ annotations }),
  addAnnotation: (annotation) => set((s) => ({
    annotations: [...s.annotations, annotation],
  })),
  setVictimMarkers: (markers) => set({ victimMarkers: markers }),
  setHazardVolumes: (volumes) => set({ hazardVolumes: volumes }),
  setCurrentFloor: (floor) => set({ currentFloor: floor }),
  setHeightSlider: (h) => set({ heightSlider: h }),
}));
