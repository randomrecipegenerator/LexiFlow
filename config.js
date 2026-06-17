// LexiFlow Unified Vercel Configuration
const API_BASE = "/api";

// Manage current firm context
const LexiContext = {
    getFirmSlug: function() {
        // 1. Check URL query param (demo/testing)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('firm')) return urlParams.get('firm');
        
        // 2. Check localStorage (persisted selection)
        return localStorage.getItem('lexiflow_firm_slug') || 'general';
    },
    setFirmSlug: function(slug) {
        localStorage.setItem('lexiflow_firm_slug', slug);
    }
};

// Helper to handle fetch with API_BASE and multi-tenancy header
async function apiFetch(endpoint, options = {}) {
    // If it's a full URL, use it as is
    if (endpoint.startsWith('http')) return fetch(endpoint, options);
    
    // Normalize path: remove leading /api if present to prevent doubling
    let path = endpoint;
    if (path.startsWith('/api')) {
        path = path.substring(4);
    }
    
    // Ensure path starts with /
    if (!path.startsWith('/')) {
        path = '/' + path;
    }
    
    const url = `${API_BASE}${path}`;
    
    // Merge headers
    const headers = options.headers || {};
    const firmSlug = LexiContext.getFirmSlug();
    const token = localStorage.getItem('lexiflow_token');
    
    if (firmSlug) {
        headers['X-Firm-Slug'] = firmSlug;
    }
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    options.headers = headers;
    return fetch(url, options);
}
