const API_BASE = 'http://localhost:8000';

const headers = () => ({
  'Content-Type': 'application/json',
  ...(localStorage.getItem('lexiflow_token')
    ? { Authorization: `Bearer ${localStorage.getItem('lexiflow_token')}` }
    : {}),
});

export const api = {
  // Matters
  getMatters: async () => {
    const res = await fetch(`${API_BASE}/matters`, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch matters: ${res.status}`);
    return res.json();
  },
  getMatter: async (id: string) => {
    const res = await fetch(`${API_BASE}/matters/${id}`, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch matter: ${res.status}`);
    return res.json();
  },

  // Depositions
  getDepositions: async (matterId: string) => {
    const res = await fetch(`${API_BASE}/matters/${matterId}/depositions`, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch depositions: ${res.status}`);
    return res.json();
  },
  getDeposition: async (id: string) => {
    const res = await fetch(`${API_BASE}/depositions/${id}`, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch deposition: ${res.status}`);
    return res.json();
  },

  // Witnesses
  getWitnesses: async (matterId: string) => {
    const res = await fetch(`${API_BASE}/matters/${matterId}/witnesses`, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch witnesses: ${res.status}`);
    return res.json();
  },

  // Contradictions
  getContradictions: async (matterId?: string) => {
    const url = matterId
      ? `${API_BASE}/contradictions?matter_id=${matterId}`
      : `${API_BASE}/contradictions`;
    const res = await fetch(url, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch contradictions: ${res.status}`);
    return res.json();
  },

  // Evidence
  getEvidence: async (matterId: string) => {
    const res = await fetch(`${API_BASE}/matters/${matterId}/evidence`, { headers: headers() });
    if (!res.ok) throw new Error(`Failed to fetch evidence: ${res.status}`);
    return res.json();
  },
};