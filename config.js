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
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    
    // Merge headers
    const headers = options.headers || {};
    const firmSlug = LexiContext.getFirmSlug();
    
    if (firmSlug) {
        headers['X-Firm-Slug'] = firmSlug;
    }
    
    options.headers = headers;
    return fetch(url, options);
}
