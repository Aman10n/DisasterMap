import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// --- Missions ---
export const getMissions = () => api.get('/missions');
export const createMission = (data) => api.post('/missions', data);
export const getMission = (id) => api.get(`/missions/${id}`);
export const transitionMission = (id, data) => api.patch(`/missions/${id}/transition`, data);
export const getMissionTimeline = (id) => api.get(`/missions/${id}/timeline`);
export const getPrecheck = (id) => api.get(`/missions/${id}/precheck`);

// --- Robots ---
export const getRobots = () => api.get('/robots');
export const sendRobotCommand = (robotId, cmd) => api.post(`/robots/${robotId}/command`, cmd);

// --- Victims ---
export const getVictims = (missionId) => api.get('/victims', { params: { mission_id: missionId } });
export const updateVictimStatus = (id, data) => api.patch(`/victims/${id}/status`, data);

// --- Hazards ---
export const getHazardZones = (missionId) => api.get('/hazards/zones', { params: { mission_id: missionId } });
export const getGasHeatmap = (missionId, gasType) => api.get(`/hazards/heatmap/${missionId}/${gasType}`);

// --- Sensors ---
export const getIoTNodes = (missionId) => api.get('/sensors/nodes', { params: { mission_id: missionId } });
export const deployNode = (data) => api.post('/sensors/deploy', data);

// --- Maps ---
export const getMapMesh = (missionId) => api.get(`/maps/${missionId}/mesh`);
export const getAnnotations = (missionId) => api.get(`/maps/${missionId}/annotations`);
export const createAnnotation = (missionId, data) => api.post(`/maps/${missionId}/annotations`, data);

// --- Teleoperation ---
export const sendVelocity = (robotId, lx, ly, az) =>
  api.post(`/teleop/${robotId}/velocity`, null, { params: { linear_x: lx, linear_y: ly, angular_z: az } });
export const sendNavGoal = (robotId, x, y) =>
  api.post(`/teleop/${robotId}/nav-goal`, null, { params: { x, y } });
export const emergencyStop = (robotId) => api.post(`/teleop/${robotId}/stop`);

// --- Parameters ---
export const getParameters = () => api.get('/parameters');
export const updateParameter = (robotId, paramName, value) =>
  api.patch(`/parameters/${robotId}`, null, { params: { param_name: paramName, value } });

// --- Reports ---
export const generateReport = (missionId) => api.get(`/reports/${missionId}/pdf`);
export const getAnalytics = (missionId) => api.get(`/reports/${missionId}/analytics`);

export default api;
