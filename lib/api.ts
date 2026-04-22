import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080';

const api = axios.create({
  baseURL: API_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`⚡ [OMNI] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ [OMNI] Success: ${response.status}`);
    return response;
  },
  (error) => {
    console.error(`❌ [OMNI] Error:`, error.message);
    return Promise.reject(error);
  }
);

// Tool execution
export async function executeTool(toolId: string, params: Record<string, any>): Promise<any> {
  const response = await api.post(`/api/v1/tools/${toolId}`, params);
  return response.data;
}

// WebSocket for streaming
export function createWebSocket(path: string): WebSocket {
  const ws = new WebSocket(`${WS_URL}${path}`);
  
  ws.onopen = () => console.log(`⚡ [WS] Connected to ${path}`);
  ws.onerror = (err) => console.error(`❌ [WS] Error:`, err);
  ws.onclose = () => console.log(`🔌 [WS] Disconnected`);
  
  return ws;
}

export { api };
export default api;