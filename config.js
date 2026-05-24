// LexiFlow Unified Vercel Configuration
const API_BASE = "/api";

// Helper to handle fetch with API_BASE
async function apiFetch(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    return fetch(url, options);
}
