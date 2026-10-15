import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// --- Players ---
export const listPlayers = (params = {}) => api.get("/api/players", { params }).then((r) => r.data);

export const getTopPlayers = (limit = 10) =>
  api.get("/api/players/top", { params: { limit } }).then((r) => r.data);

export const getPlayer = (id) => api.get(`/api/players/${id}`).then((r) => r.data);

// --- Clubs (for filter dropdowns) ---
export const getClubs = () => api.get("/api/clubs").then((r) => r.data);

// --- Prediction ---
export const predictValue = (payload) => api.post("/api/predict", payload).then((r) => r.data);

// --- Comparison ---
export const comparePlayers = (playerIdA, playerIdB) =>
  api.post("/api/compare", { player_id_a: playerIdA, player_id_b: playerIdB }).then((r) => r.data);

// --- Analytics ---
export const getAnalyticsSummary = () => api.get("/api/analytics/summary").then((r) => r.data);
export const getAnalyticsCharts = () => api.get("/api/analytics/charts").then((r) => r.data);

// --- Model metrics ---
export const getModelMetrics = () => api.get("/api/model/metrics").then((r) => r.data);

// --- Chat (FootballIQ Assistant) ---
export const sendChatMessage = (message, history = []) =>
  api.post("/api/chat", { message, history }).then((r) => r.data);
