let allLeads = [];
let statusChart = null;
let analyticsSourceChart = null;
let fdSourceChart = null;

// Initialize firm selector from context on load
document.addEventListener('DOMContentLoaded', () => {
    const slug = LexiContext.getFirmSlug();
    const firmSelect = document.getElementById('demo-firm-select');
    if (firmSelect) {
        firmSelect.value = slug;
        if (slug !== 'general') {
            const toggle = document.getElementById('demo-mode-toggle');
            if (toggle) {
                toggle.checked = true;
                firmSelect.classList.remove('d-none');
            }
        }
    }
    showSection('onboarding');
});

async function toggleDemoMode() {
    const isDemo = document.getElementById('demo-mode-toggle').checked;
    const firmSelect = document.getElementById('demo-firm-select');
    
    if (isDemo) firmSelect.classList.remove('d-none');
    else firmSelect.classList.add('d-none');

    renderLeads([]);
    
    if (isDemo) {
        const firm = firmSelect.value;
        LexiContext.setFirmSlug(firm);
        try {
            const formData = new FormData();
            formData.append('firm_slug', firm);
            await apiFetch('/demo/seed', { method: 'POST', body: formData });
            await loadLeads();
        } catch (e) { console.error("Seeding failed", e); }
    } else {
        await loadLeads();
    }
}

async function seedVoiceLead() {
    try {
        const response = await apiFetch('/demo/seed-voice', { method: 'POST' });
        if (response.ok) {
            alert("Voice AI Lead generated! Check the leads list.");
            loadLeads();
        }
    } catch (e) { console.error("Voice seed failed", e); }
}

async function loadLeads() {
    const toggle = document.getElementById('demo-mode-toggle');
    const isDemo = toggle ? toggle.checked : false;
    try {
        const firmResponse = await apiFetch('/firm/me');
        if (firmResponse.ok) {
            const firmData = await firmResponse.json();
            applyFirmBranding(firmData);
        }

        const response = await apiFetch(`/leads?demo_mode=${isDemo}`);
        allLeads = await response.json();
        updateStats();
        filterLeads();
    } catch (error) { console.error('Error loading leads:', error); }
}

function applyFirmBranding(firm) {
    const navBrand = document.querySelector('.navbar-brand');
    if (navBrand && firm.branding_logo) {
        if (firm.slug === 'clifford-law' || firm.slug === 'smith-lacien') {
            navBrand.innerHTML = `<img src="${firm.branding_logo}" alt="${firm.name}" height="45" class="py-1">`;
        } else {
            navBrand.innerHTML = `<img src="${firm.branding_logo}" alt="${firm.name}" height="32" class="me-2">${firm.name}`;
        }
    }

    if (firm.branding_colors) {
        try {
            const colors = JSON.parse(firm.branding_colors);
            if (colors.primary) {
                document.documentElement.style.setProperty('--bs-primary', colors.primary);
                document.querySelectorAll('.btn-primary').forEach(btn => {
                    btn.style.setProperty('background-color', colors.primary, 'important');
                    btn.style.setProperty('border-color', colors.primary, 'important');
                });
                document.querySelectorAll('.text-primary').forEach(el => {
                    el.style.setProperty('color', colors.primary, 'important');
                });
                document.querySelectorAll('.progress-bar.bg-primary').forEach(pb => {
                    pb.style.setProperty('background-color', colors.primary, 'important');
                });
            }
            if (colors.background && colors.background !== '#ffffff') {
                document.body.style.backgroundColor = colors.background;
            }
        } catch (e) { console.error("Error applying colors", e); }
    }
}

function updateStats() {
    const total = allLeads.length;
    const highPriority = allLeads.filter(l => l.status === 'High Priority').length;
    const avgScore = total > 0 ? (allLeads.reduce((acc, curr) => acc + (curr.score || 0), 0) / total).toFixed(1) : 0;

    document.getElementById('stat-total').innerText = total;
    document.getElementById('stat-high-priority').innerText = highPriority;
    document.getElementById('stat-avg-score').innerText = avgScore;
    const hpPercent = total > 0 ? (highPriority / total * 100) : 0;
    const progress = document.getElementById('stat-hp-progress');
    if (progress) progress.style.width = `${hpPercent}%`;
    updateChart(allLeads);
}

function updateChart(leads) {
    const chartEl = document.getElementById('statusChart');
    if (!chartEl) return;
    const ctx = chartEl.getContext('2d');
    const statusCounts = { 'High Priority': 0, 'Requires Review': 0, 'Disqualified': 0, 'New': 0 };
    leads.forEach(l => {
        if (statusCounts.hasOwnProperty(l.status)) statusCounts[l.status]++;
        else statusCounts['New']++;
    });
    const data = {
        labels: Object.keys(statusCounts),
        datasets: [{
            data: Object.values(statusCounts),
            backgroundColor: ['#198754', '#ffc107', '#dc3545', '#6c757d'],
            hoverOffset: 4,
            borderWidth: 0
        }]
    };
    if (statusChart) {
        statusChart.data = data;
        statusChart.update();
    } else {
        statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                cutout: '70%',
                plugins: {
                    legend: { display: true, position: 'right', labels: { boxWidth: 10, font: { size: 10 } } },
                    tooltip: { enabled: true }
                },
                maintainAspectRatio: false
            }
        });
    }
}

function renderLeads(leads) {
    const table = document.getElementById('leads-table');
    const emptyState = document.getElementById('empty-state');
    if (!table) return;
    table.innerHTML = '';
    if (leads.length === 0) emptyState.classList.remove('d-none');
    else emptyState.classList.add('d-none');

    leads.forEach(lead => {
        const tr = document.createElement('tr');
        if (lead.status === 'High Priority' || lead.score >= 90) tr.classList.add('priority-row');
        
        let hotBadge = lead.score >= 90 ? '<span class="badge bg-danger ms-2" style="font-size: 0.6rem;">HOT</span>' : '';
        
        tr.innerHTML = `
            <td class="ps-4 fw-bold">#${lead.id}</td>
            <td>
                <div class="fw-bold text-dark d-flex align-items-center">${lead.full_name || 'Anonymous'} ${hotBadge}</div>
                <div class="small text-muted text-truncate" style="max-width: 250px;">${lead.summary || 'No summary yet...'}</div>
            </td>
            <td><span class="badge bg-light text-dark border">${lead.source || 'Chat'}</span></td>
            <td><span class="badge ${getStatusBadge(lead.status)}">${lead.status}</span></td>
            <td><span class="badge ${getSyncBadge(lead.sync_status)}">${lead.sync_status || 'Not Synced'}</span></td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="me-2 fw-bold" style="width: 30px;">${lead.score}</span>
                    <div class="progress flex-grow-1" style="height: 6px; min-width: 80px; max-width: 120px;">
                        <div class="progress-bar ${getScoreColor(lead.score)}" role="progressbar" style="width: ${lead.score}%"></div>
                    </div>
                </div>
            </td>
            <td>
                <div class="small text-dark">${new Date(lead.created_at).toLocaleDateString()}</div>
                <div class="text-muted" style="font-size: 0.75rem;">${new Date(lead.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
            </td>
            <td class="text-end pe-4">
                <div class="btn-group">
                    <button class="btn btn-sm btn-primary px-3 rounded-start-pill dropdown-toggle" type="button" data-bs-toggle="dropdown">
                        <i class="bi bi-cloud-arrow-up me-1"></i> Sync
                    </button>
                    <ul class="dropdown-menu shadow border-0">
                        <li><a class="dropdown-item small" href="#" onclick="syncToSystem(${lead.id}, 'clio')"><i class="bi bi-box-fill me-2 text-warning"></i> Clio Grow</a></li>
                        <li><a class="dropdown-item small" href="#" onclick="syncToSystem(${lead.id}, 'mycase')"><i class="bi bi-briefcase-fill me-2 text-primary"></i> MyCase</a></li>
                        <li><a class="dropdown-item small" href="#" onclick="syncToSystem(${lead.id}, 'filevine')"><i class="bi bi-leaf-fill me-2 text-success"></i> Filevine</a></li>
                    </ul>
                    <button class="btn btn-sm btn-white border shadow-sm px-3 rounded-end-pill" onclick="viewLead(${lead.id})">View Case</button>
                </div>
            </td>
        `;
        table.appendChild(tr);
    });
}

function filterLeads() {
    const status = document.getElementById('filter-status').value;
    const minScore = document.getElementById('filter-score').value;
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    let filtered = allLeads;
    if (status) filtered = filtered.filter(l => l.status === status);
    if (minScore) filtered = filtered.filter(l => (l.score || 0) >= parseInt(minScore));
    if (searchTerm) {
        filtered = filtered.filter(l => 
            (l.full_name && l.full_name.toLowerCase().includes(searchTerm)) ||
            (l.summary && l.summary.toLowerCase().includes(searchTerm)) ||
            (l.id.toString().includes(searchTerm))
        );
    }
    renderLeads(filtered);
}

function getStatusBadge(status) {
    if (status === 'High Priority') return 'bg-success';
    if (status === 'Requires Review') return 'bg-warning text-dark';
    if (status === 'Disqualified') return 'bg-danger';
    if (status === 'Document Analysis') return 'bg-info text-dark';
    return 'bg-secondary';
}

function getSyncBadge(status) {
    if (!status || status === 'Not Synced') return 'bg-light text-muted border';
    if (status.includes('Synced')) return 'bg-primary';
    if (status === 'Error') return 'bg-danger';
    return 'bg-secondary';
}

function getScoreColor(score) {
    if (score >= 80) return 'bg-success';
    if (score >= 50) return 'bg-warning';
    return 'bg-danger';
}

async function viewLead(id) {
    try {
        const response = await apiFetch(`/leads/${id}`);
        const lead = await response.json();
        document.getElementById('modal-lead-id').value = lead.id;
        document.getElementById('modal-name').innerText = lead.full_name || `Lead #${lead.id}`;
        document.getElementById('modal-summary').innerText = lead.summary || 'No summary available.';
        
        document.getElementById('modal-transcript').innerHTML = lead.messages.map(m => `
            <div class="mb-3 d-flex flex-column ${m.role === 'user' ? 'align-items-end' : 'align-items-start'}">
                <div class="small fw-bold text-muted mb-1 mx-2" style="font-size: 0.7rem;">${m.role === 'user' ? 'CLIENT' : 'LexiFlow Technologies Inc'}</div>
                <div class="p-3 rounded-4 shadow-sm ${m.role === 'user' ? 'bg-primary text-white' : 'bg-white border text-dark'}" style="max-width: 85%; border-radius: 15px !important;">
                    ${m.content}
                </div>
                <div class="text-muted mt-1 mx-2" style="font-size: 0.65rem;">${new Date(m.time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
            </div>
        `).join('');

        document.getElementById('modal-docs').innerHTML = lead.documents.map(d => `
            <div class="card mb-2 border-0 bg-light p-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                        <i class="bi ${d.filename.toLowerCase().endsWith('.pdf') ? 'bi-file-earmark-pdf-fill text-danger' : 'bi-file-earmark-image-fill text-primary'} fs-4 me-2"></i>
                        <div><div class="small fw-bold text-dark">${d.filename}</div><div class="text-muted small">${d.analysis ? d.analysis.document_type : 'Document'}</div></div>
                    </div>
                    <button class="btn btn-sm btn-outline-secondary" onclick="alert('In production, this opens the file.')">View</button>
                </div>
                ${d.analysis ? `
                    <div class="mt-2 p-2 bg-white rounded border small">
                        <div class="fw-bold text-primary mb-1">Extracted Data:</div>
                        ${Object.entries(d.analysis.extracted_fields).map(([k, v]) => `<div><strong>${k}:</strong> ${v}</div>`).join('')}
                        <div class="text-muted mt-1 italic">${d.analysis.summary || ''}</div>
                    </div>
                ` : ''}
            </div>
        `).join('') || '<div class="text-center py-3 text-muted">No documents uploaded.</div>';
        
        renderModalInvoices(lead.invoices);

        const esignBadge = document.getElementById('esign-status-badge');
        if (lead.esign_status && lead.esign_status !== 'Not Sent') {
            document.getElementById('esign-status-container').classList.remove('d-none');
            esignBadge.innerText = lead.esign_status;
            esignBadge.className = `badge ${lead.esign_status === 'Signed' ? 'bg-success' : 'bg-info'}`;
        } else {
            document.getElementById('esign-status-container').classList.add('d-none');
        }

        document.getElementById('modal-case-value').innerText = lead.case_value ? '$' + lead.case_value.toLocaleString() : '$0.00';
        runConflictCheck(lead.id);

        if (lead.demand_draft) {
            document.getElementById('demand-letter-preview').classList.remove('d-none');
            document.getElementById('demand-preview-text').innerText = lead.demand_draft;
        } else {
            document.getElementById('demand-letter-preview').classList.add('d-none');
        }

        const syncBadge = document.getElementById('sync-status-badge');
        if (lead.sync_status && lead.sync_status !== 'Not Synced') {
            document.getElementById('sync-status-container').classList.remove('d-none');
            syncBadge.innerText = lead.sync_status;
            syncBadge.className = `badge ${getSyncBadge(lead.sync_status)}`;
            document.getElementById('external-id-text').innerText = lead.external_crm_id ? `(ID: ${lead.external_crm_id})` : '';
        } else {
            document.getElementById('sync-status-container').classList.add('d-none');
        }
        
        new bootstrap.Modal(document.getElementById('leadModal')).show();
    } catch (e) { console.error("Error loading lead", e); }
}

async function runConflictCheck(id) {
    const statusEl = document.getElementById('modal-conflict-status');
    statusEl.innerText = 'Checking...';
    statusEl.className = 'badge bg-secondary';
    try {
        const response = await apiFetch(`/leads/${id}/conflict-check`);
        const result = await response.json();
        statusEl.innerText = result.status;
        statusEl.className = `badge ${result.status === 'Clear' ? 'bg-success' : 'bg-danger'}`;
    } catch (e) { console.error("Conflict check failed", e); }
}

function renderModalInvoices(invoices) {
    document.getElementById('modal-invoices').innerHTML = invoices.map(i => `
        <li class="list-group-item d-flex justify-content-between align-items-center bg-light border-0 mb-1 rounded">
            <div><div class="fw-bold">${getCurrencySymbol(i.currency)}${i.amount.toFixed(2)}</div><div class="text-muted small">${new Date(i.date).toLocaleDateString()}</div></div>
            <span class="badge ${i.status === 'Paid' ? 'bg-success' : 'bg-warning'}">${i.status}</span>
        </li>
    `).join('') || '<div class="text-center py-2 text-muted small">No payment requests yet.</div>';
}

function getCurrencySymbol(curr) { return curr === 'EUR' ? '€' : '$'; }

async function loadUsage() {
    try {
        const response = await apiFetch('/billing/usage');
        if (!response.ok) return;
        const data = await response.json();
        
        const planEl = document.getElementById('billing-plan-status');
        const trialEl = document.getElementById('billing-trial-expires');
        if (planEl) planEl.innerText = data.plan_status;
        if (trialEl) trialEl.innerText = data.trial_expires_at ? `Expires: ${new Date(data.trial_expires_at).toLocaleDateString()}` : 'No expiry';
            
        const docUsageEl = document.getElementById('usage-docs');
        const voiceUsageEl = document.getElementById('usage-voice');
        const webUsageEl = document.getElementById('usage-web');
        const emailUsageEl = document.getElementById('usage-email');
        
        if (docUsageEl) docUsageEl.innerText = data.totals.document_analysis || 0;
        if (voiceUsageEl) voiceUsageEl.innerText = (data.totals.voice_minutes || 0).toFixed(2);
        
        const webTotal = (data.totals.web_intake || 0) + (data.totals.form_intake || 0) + (data.totals.receptionist_intake || 0);
        if (webUsageEl) webUsageEl.innerText = webTotal;
        if (emailUsageEl) emailUsageEl.innerText = data.totals.email_intake || 0;
        
        const totalIntakes = webTotal + (data.totals.email_intake || 0) + (data.totals.voice_minutes || 0) / 10;
        const roi = totalIntakes * 2.5 * 300;
        const roiEl = document.getElementById('usage-roi');
        if (roiEl) roiEl.innerText = '$' + roi.toLocaleString();
    } catch (e) { console.error("Error loading usage", e); }
}

async function loadInvoices() {
    try {
        const response = await apiFetch('/billing/invoices');
        const invoices = await response.json();
        const table = document.getElementById('invoices-table');
        if (table) {
            table.innerHTML = invoices.map(inv => `
                <tr>
                    <td class="ps-4">#${inv.id}</td>
                    <td>Lead #${inv.lead_id}</td>
                    <td class="fw-bold">${getCurrencySymbol(inv.currency)}${inv.amount.toFixed(2)}</td>
                    <td><span class="badge ${inv.status === 'Paid' ? 'bg-success' : 'bg-warning'}">${inv.status}</span></td>
                    <td>${new Date(inv.created_at).toLocaleDateString()}</td>
                    <td class="text-end pe-4">
                        ${inv.status === 'Pending' ? `<button class="btn btn-sm btn-outline-success rounded-pill px-3" onclick="syncLawPay(${inv.id})">Sync LawPay</button>` : `<button class="btn btn-sm btn-light disabled rounded-pill px-3">Completed</button>`}
                    </td>
                </tr>
            `).join('') || '<tr><td colspan="6" class="text-center py-4">No invoices found.</td></tr>';
        }
    } catch (e) { console.error("Error loading invoices", e); }
}

async function syncLawPay(id) {
    try {
        const response = await apiFetch(`/billing/sync/lawpay/${id}`, { method: 'POST' });
        const result = await response.json();
        alert(result.message);
        loadInvoices();
    } catch (e) { console.error("Sync failed", e); }
}

async function requestPayment() {
    const leadId = document.getElementById('modal-lead-id').value;
    const amount = document.getElementById('request-amount').value;
    const currency = document.getElementById('request-currency').value;
    if (!amount) return alert("Please enter an amount");
    const formData = new FormData();
    formData.append('lead_id', leadId);
    formData.append('amount', amount);
    formData.append('currency', currency);
    formData.append('description', 'Retainer Request');
    try {
        const response = await apiFetch('/billing/invoices', { method: 'POST', body: formData });
        if (response.ok) {
            alert("Payment request sent!");
            document.getElementById('request-amount').value = '';
            const leadResponse = await apiFetch(`/leads/${leadId}`);
            const lead = await leadResponse.json();
            renderModalInvoices(lead.invoices);
        }
    } catch (e) { console.error("Request failed", e); }
}

async function sendRetainer() {
    const leadId = document.getElementById('modal-lead-id').value;
    try {
        const response = await apiFetch(`/esign/send/${leadId}`, { method: 'POST' });
        if (response.ok) {
            const result = await response.json();
            alert(`Retainer sent! Request ID: ${result.signature_request_id}`);
            const leadResponse = await apiFetch(`/leads/${leadId}`);
            const lead = await leadResponse.json();
            const esignContainer = document.getElementById('esign-status-container');
            const esignBadge = document.getElementById('esign-status-badge');
            esignContainer.classList.remove('d-none');
            esignBadge.innerText = lead.esign_status;
            esignBadge.className = 'badge bg-info';
        }
    } catch (e) { console.error("eSign Request failed", e); }
}

async function loadAuditLogs() {
    try {
        const response = await apiFetch('/audit-logs');
        const logs = await response.json();
        const table = document.getElementById('audit-logs-table');
        if (table) {
            table.innerHTML = logs.map(log => `
                <tr>
                    <td class="ps-3"><span class="badge bg-light text-dark border">${log.action}</span></td>
                    <td>${log.lead_id || '-'}</td>
                    <td class="text-wrap" style="max-width: 300px;">${log.details || ''}</td>
                    <td class="text-muted">${new Date(log.timestamp).toLocaleString()}</td>
                </tr>
            `).join('');
        }
    } catch (e) { console.error("Error loading audit logs", e); }
}

async function loadAnalytics() {
    try {
        const response = await apiFetch('/analytics/overview');
        if (!response.ok) return;
        const data = await response.json();
        
        document.getElementById('analytics-conversion-rate').innerText = data.conversion_rate + '%';
        document.getElementById('analytics-pipeline-value').innerText = '$' + data.total_pipeline_value.toLocaleString();
        document.getElementById('analytics-total-leads').innerText = data.total_leads;

        const ctx = document.getElementById('analyticsSourceChart').getContext('2d');
        const labels = Object.keys(data.source_breakdown);
        const counts = Object.values(data.source_breakdown);
        const chartData = { 
            labels: labels, 
            datasets: [{ 
                label: 'Leads by Source', 
                data: counts, 
                backgroundColor: ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#db2777'], 
                borderWidth: 0, 
                borderRadius: 4 
            }] 
        };
        if (analyticsSourceChart) { 
            analyticsSourceChart.data = chartData; 
            analyticsSourceChart.update(); 
        } else { 
            analyticsSourceChart = new Chart(ctx, { 
                type: 'bar', 
                data: chartData, 
                options: { 
                    indexAxis: 'y', 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    plugins: { legend: { display: false } }, 
                    scales: { x: { beginAtZero: true, grid: { color: '#f1f5f9' } }, y: { grid: { display: false } } } 
                } 
            }); 
        }

        const hotLeadsContainer = document.getElementById('analytics-hot-leads');
        if (data.hot_leads.length === 0) { 
            hotLeadsContainer.innerHTML = '<div class="p-4 text-center text-muted small">No hot leads identified yet.</div>'; 
        } else { 
            hotLeadsContainer.innerHTML = data.hot_leads.map(lead => `
                <div class="list-group-item p-3 border-0 border-bottom">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <div class="fw-bold text-dark">${lead.full_name}</div>
                        <span class="badge bg-danger rounded-pill">${lead.score}</span>
                    </div>
                    <div class="small text-muted mb-2">${lead.case_type}</div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="small text-muted" style="font-size: 0.7rem;">${new Date(lead.created_at).toLocaleDateString()}</div>
                        <button class="btn btn-sm btn-outline-primary py-0 px-2 small" style="font-size: 0.7rem;" onclick="viewLead(${lead.id})">Details</button>
                    </div>
                </div>
            `).join(''); 
        }
    } catch (e) { console.error("Error loading analytics", e); }
}

window.showSection = function(section) {
    ['leads', 'analytics', 'forms', 'billing', 'marketplace', 'front-desk', 'settings', 'onboarding', 'reports', 'integrations'].forEach(s => {
        const el = document.getElementById('section-' + s);
        if (el) el.classList.add('d-none');
    });
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    const target = document.getElementById('section-' + section);
    if (target) target.classList.remove('d-none');
    const nav = document.getElementById('nav-' + section);
    if (nav) nav.classList.add('active');

    if (section === 'onboarding') loadOnboarding();
    if (section === 'leads') loadLeads();
    if (section === 'analytics') loadAnalytics();
    if (section === 'billing') { loadInvoices(); loadUsage(); }
    if (section === 'reports') loadReports();
    if (section === 'front-desk') loadFrontDeskSettings();
    if (section === 'integrations') loadIntegrations();
    if (section === 'settings') {
        loadAuditLogs();
        loadKB();
        loadCRMSettings();
        loadGitHubSettings();
        loadPostmarkSettings();
        loadBillingSettings();
        document.getElementById('webhook-url').value = API_BASE + '/api/reception/webhook';
    }
};

async function loadBillingSettings() {
    try {
        const response = await apiFetch('/firm/me');
        const data = await response.json();
        const apiConfig = data.api_config || {};
        document.getElementById('settings-stripe-secret').value = apiConfig.stripe_secret_key || '';
        document.getElementById('settings-stripe-public').value = apiConfig.stripe_public_key || '';
    } catch (e) { console.error("Error loading billing settings", e); }
}

async function saveBillingSettings() {
    const currentResp = await apiFetch('/firm/me');
    const currentData = await currentResp.json();
    const apiConfig = currentData.api_config || {};
    apiConfig.stripe_secret_key = document.getElementById('settings-stripe-secret').value;
    apiConfig.stripe_public_key = document.getElementById('settings-stripe-public').value;
    const formData = new FormData();
    formData.append('api_config', JSON.stringify(apiConfig));
    try {
        const response = await apiFetch('/firm/settings', { method: 'POST', body: formData });
        if (response.ok) alert("Billing settings saved successfully");
    } catch (e) { console.error("Error saving billing settings", e); }
}

async function loadFrontDeskSettings() {
    try {
        const response = await apiFetch('/firm/me');
        const firm = await response.json();
        document.getElementById('voiceToggle').checked = firm.voice_enabled === 1;
        document.getElementById('voiceGreeting').value = firm.voice_config.greeting || "Hello, and thank you for calling. I am your AI intake assistant. How can I help you today?";
        const voiceId = firm.voice_config.voice_id || 'sarah';
        document.querySelectorAll('.voice-card').forEach(card => card.classList.toggle('selected', card.dataset.voiceId === voiceId));
        document.getElementById('emailToggle').checked = firm.email_enabled === 1;
        document.getElementById('fd-email-address').innerText = `intake+${firm.slug}@lexiflow.co`;
        document.getElementById('emailAutoReply').value = firm.email_config.template || "Thank you for reaching out. We have received your inquiry and will review it shortly.\n\nThis is an automated response from LexiFlow Technologies Inc.";
        renderActiveHours(firm.active_hours);
        updateFrontDeskAnalytics();
    } catch (e) { console.error("Error loading Front Desk settings", e); }
}

function renderActiveHours(hours) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const grid = document.getElementById('fd-hours-grid');
    if (!grid) return;
    grid.innerHTML = `<div class="day-label fw-bold text-muted small text-uppercase mb-1">Day</div><div class="text-center fw-bold text-muted small text-uppercase mb-1">Open</div><div class="text-center fw-bold text-muted small text-uppercase mb-1">Close</div>`;
    days.forEach(day => {
        const dayKey = day.toLowerCase();
        const dayHours = (hours && hours[dayKey]) || { open: "09:00", close: "17:00", active: true };
        const row = document.createElement('div');
        row.className = 'contents';
        row.innerHTML = `<div class="day-label"><div class="form-check form-switch mb-0 d-inline-block"><input class="form-check-input hour-toggle" type="checkbox" id="toggle-${dayKey}" ${dayHours.active ? 'checked' : ''}></div>${day}</div><div><input type="time" class="form-control form-control-sm time-input open-time" value="${dayHours.open}" ${!dayHours.active ? 'disabled' : ''}></div><div><input type="time" class="form-control form-control-sm time-input close-time" value="${dayHours.close}" ${!dayHours.active ? 'disabled' : ''}></div>`;
        Array.from(row.children).forEach(child => grid.appendChild(child));
    });
}

async function saveFrontDeskSettings() {
    const btn = document.querySelector('#section-front-desk .btn-primary');
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';
    try {
        const voiceConfig = { 
            voice_id: document.querySelector('.voice-card.selected')?.dataset.voiceId || 'sarah', 
            greeting: document.getElementById('voiceGreeting').value 
        };
        const emailConfig = { template: document.getElementById('emailAutoReply').value };
        const activeHours = {};
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        const hourToggles = document.querySelectorAll('.hour-toggle');
        const openTimes = document.querySelectorAll('.open-time');
        const closeTimes = document.querySelectorAll('.close-time');
        days.forEach((day, i) => { activeHours[day] = { active: hourToggles[i].checked, open: openTimes[i].value, close: closeTimes[i].value }; });
        
        const formData = new FormData();
        formData.append('voice_enabled', document.getElementById('voiceToggle').checked ? 1 : 0);
        formData.append('voice_config', JSON.stringify(voiceConfig));
        formData.append('email_enabled', document.getElementById('emailToggle').checked ? 1 : 0);
        formData.append('email_config', JSON.stringify(emailConfig));
        formData.append('active_hours', JSON.stringify(activeHours));
        const response = await apiFetch('/firm/settings', { method: 'POST', body: formData });
        if (response.ok) alert("Front Desk settings saved!");
        else alert("Failed to save settings.");
    } catch (e) { alert("Error saving settings."); } finally { btn.innerHTML = originalHtml; }
}

function updateFrontDeskAnalytics() {
    const sources = { 'Chat': 0, 'Voice AI': 0, 'Email': 0 };
    allLeads.forEach(l => {
        const s = l.source || 'Chat';
        if (sources.hasOwnProperty(s)) sources[s]++;
        else sources['Chat']++;
    });
    const total = allLeads.length;
    const voiceCount = sources['Voice AI'] || 0;
    const emailCount = sources['Email'] || 0;
    const webCount = sources['Chat'] || 0;
    const rate = total > 0 ? Math.round((allLeads.filter(l => l.status === 'High Priority').length / total) * 100) : 0;
    
    if (document.getElementById('fd-stat-voice')) document.getElementById('fd-stat-voice').innerText = voiceCount;
    if (document.getElementById('fd-stat-email')) document.getElementById('fd-stat-email').innerText = emailCount;
    if (document.getElementById('fd-stat-web')) document.getElementById('fd-stat-web').innerText = webCount;
    if (document.getElementById('fd-stat-rate')) document.getElementById('fd-stat-rate').innerText = rate + '%';
    
    const chartEl = document.getElementById('fdLeadSourceChart');
    if (chartEl) {
        const ctx = chartEl.getContext('2d');
        const chartData = { labels: ['Web Chat', 'Voice AI', 'Email'], datasets: [{ data: [webCount, voiceCount, emailCount], backgroundColor: ['#2563eb', '#16a34a', '#d97706'], borderWidth: 0 }] };
        if (fdSourceChart) { fdSourceChart.data = chartData; fdSourceChart.update(); }
        else { fdSourceChart = new Chart(ctx, { type: 'doughnut', data: chartData, options: { cutout: '70%', plugins: { legend: { display: false } }, maintainAspectRatio: false } }); }
    }
    
    const legendEl = document.getElementById('fd-source-legend');
    if (legendEl) {
        legendEl.innerHTML = `<div class="d-flex justify-content-between align-items-center py-2 border-bottom"><div><span class="source-badge web"><i class="bi bi-globe2"></i>Web Chat</span></div><div class="fw-bold">${webCount}</div></div><div class="d-flex justify-content-between align-items-center py-2 border-bottom"><div><span class="source-badge voice"><i class="bi bi-telephone"></i>Voice AI</span></div><div class="fw-bold">${voiceCount}</div></div><div class="d-flex justify-content-between align-items-center py-2"><div><span class="source-badge email"><i class="bi bi-envelope"></i>Email</span></div><div class="fw-bold">${emailCount}</div></div>`;
    }
    
    const activityEl = document.getElementById('fd-recent-activity');
    if (activityEl) {
        activityEl.innerHTML = allLeads.slice(0, 5).map(l => `<div class="list-group-item px-3 py-2 border-0"><div class="d-flex align-items-start gap-2"><i class="bi ${l.source === 'Voice AI' ? 'bi-telephone text-success' : (l.source === 'Email' ? 'bi-envelope text-warning' : 'bi-globe2 text-primary')} mt-1"></i><div class="flex-grow-1"><div class="small fw-bold">${l.full_name}</div><div class="small text-muted text-truncate" style="max-width: 180px;">${l.summary || 'Processing...'}</div><div class="small text-muted" style="font-size:0.65rem;">${new Date(l.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div></div>${l.status === 'High Priority' ? '<span class="badge bg-danger rounded-pill" style="font-size:0.5rem;">Priority</span>' : ''}</div></div>`).join('') || '<div class="p-3 text-center text-muted small">No recent activity.</div>';
    }
}

async function loadKB() { 
    try { 
        const response = await apiFetch('/knowledge-base'); 
        const kb = await response.json(); 
        const listEl = document.getElementById('kb-list');
        if (listEl) {
            listEl.innerHTML = kb.map(item => `<div class="list-group-item"><div class="d-flex justify-content-between align-items-start"><div class="fw-bold">${item.title}</div><button class="btn btn-sm btn-link text-danger p-0" onclick="deleteKB(${item.id})"><i class="bi bi-trash"></i></button></div><div class="small text-muted mt-1">${item.content}</div><div class="text-muted italic mt-1" style="font-size: 0.65rem;">Added ${new Date(item.created_at).toLocaleDateString()}</div></div>`).join('') || '<div class="p-4 text-center text-muted">No context entries yet.</div>'; 
        }
    } catch (e) { console.error("Error loading KB", e); } 
}

async function saveKB() { 
    const title = document.getElementById('kb-title').value; 
    const content = document.getElementById('kb-content').value; 
    if (!title || !content) return alert("Title and content required"); 
    const formData = new FormData(); 
    formData.append('title', title); 
    formData.append('content', content); 
    try { 
        const response = await apiFetch('/knowledge-base', { method: 'POST', body: formData }); 
        if (response.ok) { 
            alert("Knowledge Base entry added!"); 
            document.getElementById('kb-title').value = ''; 
            document.getElementById('kb-content').value = ''; 
            loadKB(); 
        } 
    } catch (e) { console.error("KB Save failed", e); } 
}

async function deleteKB(id) { 
    if (!confirm("Remove this entry from AI context?")) return; 
    try { 
        const response = await apiFetch(`/knowledge-base/${id}`, { method: 'DELETE' }); 
        if (response.ok) { alert("Entry removed."); loadKB(); } 
    } catch (e) { console.error("Delete failed", e); } 
}

async function syncToSystem(leadId, system) { 
    const btn = event ? event.target.closest('button') : null; 
    const originalHtml = btn ? btn.innerHTML : ''; 
    if (btn) btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Syncing...'; 
    try { 
        const response = await apiFetch(`/sync/${system}/${leadId}`, { method: 'POST' }); 
        const result = await response.json(); 
        if (result.status === 'success') { 
            loadLeads(); 
            document.getElementById('sync-system-name').innerText = `Target System: ${system.charAt(0).toUpperCase() + system.slice(1)} ${system === 'clio' ? 'Grow' : ''}`; 
            document.getElementById('sync-payload-display').innerText = JSON.stringify(result.payload_sent, null, 2); 
            new bootstrap.Modal(document.getElementById('syncResultModal')).show(); 
            if (btn) { btn.innerHTML = '<i class="bi bi-check2-all me-1"></i>Synced'; btn.className = btn.className.replace('btn-primary', 'btn-success'); } 
        } else { alert(`Sync failed: ${result.message}`); if (btn) btn.innerHTML = originalHtml; } 
    } catch (e) { alert("Sync failed. See console for details."); if (btn) btn.innerHTML = originalHtml; } 
}

async function draftDemandLetter() { 
    const leadId = document.getElementById('modal-lead-id').value; 
    const btn = event.target.closest('button'); 
    const originalText = btn.innerHTML; 
    btn.disabled = true; 
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Drafting...'; 
    try { 
        const response = await apiFetch(`/leads/${leadId}/draft-demand`, { method: 'POST' }); 
        const result = await response.json(); 
        document.getElementById('demand-letter-preview').classList.remove('d-none'); 
        document.getElementById('demand-preview-text').innerText = result.draft; 
        alert("Demand letter drafted successfully!"); 
    } catch (e) { alert("Failed to draft demand letter."); } 
    finally { btn.disabled = false; btn.innerHTML = originalText; } 
}

async function generateMedicalChronology() { 
    const leadId = document.getElementById('modal-lead-id').value; 
    const btn = event.target.closest('button'); 
    const originalText = btn.innerHTML; 
    btn.disabled = true; 
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Analyzing...'; 
    try { 
        const response = await apiFetch(`/leads/${leadId}/medical-chronology`); 
        const result = await response.json(); 
        let html = '<table class="table table-sm table-bordered mt-2 small"><thead><tr><th>Date</th><th>Event</th><th>Details</th></tr></thead><tbody>'; 
        result.chronology.forEach(item => { html += `<tr><td>${item.date}</td><td>${item.event}</td><td>${item.details}</td></tr>`; }); 
        html += '</tbody></table>'; 
        const summaryArea = document.getElementById('modal-summary'); 
        const originalSummary = summaryArea.innerText; 
        summaryArea.innerHTML = `<strong>Medical Chronology:</strong><br>${html}<hr><strong>Original Summary:</strong><br>${originalSummary}`; 
        alert("Medical Chronology generated and added to summary view!"); 
    } catch (e) { alert("Failed to generate chronology."); } 
    finally { btn.disabled = false; btn.innerHTML = originalText; } 
}

async function loadCRMSettings() {
    try {
        const response = await apiFetch('/firm/me');
        const data = await response.json();
        const toggle = document.getElementById('productionSyncToggle');
        if (toggle) toggle.checked = data.production_sync_enabled === 1;
        const apiConfig = data.api_config || {};
        if (document.getElementById('filevine-api-key')) document.getElementById('filevine-api-key').value = apiConfig.filevine_api_key || '';
        if (document.getElementById('filevine-api-secret')) document.getElementById('filevine-api-secret').value = apiConfig.filevine_api_secret || '';
        if (document.getElementById('filevine-session-id')) document.getElementById('filevine-session-id').value = apiConfig.filevine_session_id || '';
        const clioStatus = document.getElementById('clio-status');
        if (clioStatus) {
            clioStatus.innerText = apiConfig.clio_oauth_token ? "Connected" : "Not Connected";
            if (apiConfig.clio_oauth_token) { clioStatus.classList.remove('text-muted'); clioStatus.classList.add('text-success'); }
        }

        const integrationsResp = await apiFetch('/firm/integrations');
        const integrations = await integrationsResp.json();
        integrations.forEach(integ => {
            if (integ.crm_system === 'clio') {
                const autoSync = document.getElementById('clio-auto-sync-toggle');
                if (autoSync) autoSync.checked = integ.auto_sync_enabled === 1;
            } else if (integ.crm_system === 'filevine') {
                const autoSync = document.getElementById('filevine-auto-sync-toggle');
                if (autoSync) autoSync.checked = integ.auto_sync_enabled === 1;
            }
        });
    } catch (e) { console.error("Error loading CRM settings", e); }
}

async function saveCRMSettings() {
    const currentResp = await apiFetch('/firm/me');
    const currentData = await currentResp.json();
    const apiConfig = currentData.api_config || {};
    apiConfig.filevine_api_key = document.getElementById('filevine-api-key').value;
    apiConfig.filevine_api_secret = document.getElementById('filevine-api-secret').value;
    apiConfig.filevine_session_id = document.getElementById('filevine-session-id').value;
    const formData = new FormData();
    formData.append('production_sync_enabled', document.getElementById('productionSyncToggle').checked ? 1 : 0);
    formData.append('api_config', JSON.stringify(apiConfig));
    try {
        await apiFetch('/firm/settings', { method: 'POST', body: formData });
        
        const clioFormData = new FormData();
        clioFormData.append('crm_system', 'clio');
        clioFormData.append('auto_sync_enabled', document.getElementById('clio-auto-sync-toggle').checked ? 1 : 0);
        await apiFetch('/firm/integrations', { method: 'POST', body: clioFormData });

        const fvFormData = new FormData();
        fvFormData.append('crm_system', 'filevine');
        fvFormData.append('auto_sync_enabled', document.getElementById('filevine-auto-sync-toggle').checked ? 1 : 0);
        await apiFetch('/firm/integrations', { method: 'POST', body: fvFormData });

        alert("CRM Settings saved successfully");
    } catch (e) { console.error("Error saving CRM settings", e); }
}

async function loadGitHubSettings() {
    try {
        const response = await apiFetch('/firm/me');
        const data = await response.json();
        const apiConfig = data.api_config || {};
        document.getElementById('github-token').value = apiConfig.github_token || '';
        document.getElementById('github-repo').value = apiConfig.github_repo || '';
        document.getElementById('github-branch').value = apiConfig.github_branch || 'main';
    } catch (e) { console.error("Error loading GitHub settings", e); }
}

async function saveGitHubSettings() {
    const currentResp = await apiFetch('/firm/me');
    const currentData = await currentResp.json();
    const apiConfig = currentData.api_config || {};
    apiConfig.github_token = document.getElementById('github-token').value;
    apiConfig.github_repo = document.getElementById('github-repo').value;
    apiConfig.github_branch = document.getElementById('github-branch').value;
    const formData = new FormData();
    formData.append('api_config', JSON.stringify(apiConfig));
    try {
        const response = await apiFetch('/firm/settings', { method: 'POST', body: formData });
        if (response.ok) alert("GitHub Settings saved successfully");
    } catch (e) { console.error("Error saving GitHub settings", e); }
}

async function loadPostmarkSettings() {
    try {
        const response = await apiFetch('/firm/me');
        const data = await response.json();
        const apiConfig = data.api_config || {};
        document.getElementById('postmark-token').value = apiConfig.postmark_api_key || '';
        document.getElementById('postmark-recipient').value = apiConfig.postmark_recipient_email || '';
    } catch (e) { console.error("Error loading Postmark settings", e); }
}

async function savePostmarkSettings() {
    const currentResp = await apiFetch('/firm/me');
    const currentData = await currentResp.json();
    const apiConfig = currentData.api_config || {};
    apiConfig.postmark_api_key = document.getElementById('postmark-token').value;
    apiConfig.postmark_recipient_email = document.getElementById('postmark-recipient').value;
    const formData = new FormData();
    formData.append('api_config', JSON.stringify(apiConfig));
    try {
        const response = await apiFetch('/firm/settings', { method: 'POST', body: formData });
        if (response.ok) alert("Postmark Settings saved successfully");
    } catch (e) { console.error("Error saving Postmark settings", e); }
}

async function exportToGitHub() {
    const leadId = document.getElementById('modal-lead-id').value;
    const repo = document.getElementById('github-repo')?.value;
    if (!repo) return alert("Please configure GitHub repository in Settings first.");
    
    const summary = document.getElementById('modal-summary').innerText;
    const name = document.getElementById('modal-name').innerText;
    const content = `# Case Summary: ${name}\n\n${summary}`;
    const path = `exports/lead_${leadId}.md`;
    
    const formData = new FormData();
    formData.append('repo', repo);
    formData.append('path', path);
    formData.append('content', content);
    formData.append('commit_message', `Export lead ${leadId} summary`);
    
    const btn = event.target.closest('button');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Exporting...';
    
    try {
        const response = await apiFetch('/integrations/github/push', { method: 'POST', body: formData });
        const result = await response.json();
        if (result.status === 'success') {
            alert(`Exported to GitHub successfully!\nURL: ${result.url}`);
        } else {
            alert(`GitHub Export failed: ${result.message}`);
        }
    } catch (e) { alert("GitHub Export failed. See console for details."); }
    finally { btn.disabled = false; btn.innerHTML = originalHtml; }
}

async function loadOnboarding() {
    try {
        const response = await apiFetch('/firm/onboarding');
        const data = await response.json();
        const progressBar = document.getElementById('onboarding-progress-bar');
        const progressPercent = document.getElementById('onboarding-progress-percent');
        if (progressBar) progressBar.style.width = data.overall_progress + '%';
        if (progressPercent) progressPercent.innerText = data.overall_progress + '%';
        
        const container = document.getElementById('onboarding-checklist');
        if (container) {
            container.innerHTML = data.checklist.map(item => {
                const iconClass = item.status === 'completed' ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted opacity-50';
                return `
                    <div class="list-group-item border-0 px-0 py-3 d-flex align-items-center gap-3">
                        <div class="h3 mb-0"><i class="bi ${iconClass}"></i></div>
                        <div class="flex-grow-1">
                            <h6 class="fw-bold mb-1 ${item.status === 'completed' ? 'text-muted text-decoration-line-through' : ''}">${item.title}</h6>
                            <p class="small text-muted mb-0">${item.description}</p>
                        </div>
                        <div>
                            <button class="btn btn-sm ${item.status === 'completed' ? 'btn-outline-secondary' : 'btn-outline-primary'} rounded-pill px-3" onclick="showSection('${item.action_link}')">
                                ${item.action_text}
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        updateIndicator('status-github', data.checklist.find(i => i.id === 'github')?.status);
        updateIndicator('status-postmark', data.checklist.find(i => i.id === 'postmark')?.status);
        updateIndicator('status-domain', data.checklist.find(i => i.id === 'domain')?.status);
    } catch (e) { console.error("Error loading onboarding data", e); }
}

function updateIndicator(id, status) {
    const el = document.getElementById(id);
    if (!el) return;
    if (status === 'completed') {
        el.innerText = 'Connected'; el.className = 'small text-success fw-bold mb-2';
    } else {
        el.innerText = 'Disconnected'; el.className = 'small text-muted mb-2';
    }
}

function showQuickConnect(type) {
    const modal = new bootstrap.Modal(document.getElementById('quickConnectModal'));
    const title = document.getElementById('quickConnectTitle');
    ['github', 'postmark', 'domain'].forEach(t => document.getElementById(`quick-connect-${t}`).classList.add('d-none'));
    document.getElementById(`quick-connect-${type}`).classList.remove('d-none');
    if (type === 'github') title.innerText = 'Connect GitHub';
    if (type === 'postmark') title.innerText = 'Connect Postmark';
    if (type === 'domain') title.innerText = 'Verify Domain';
    modal.show();
}

async function saveQuickConnect(type) {
    const currentResp = await apiFetch('/firm/me');
    const currentData = await currentResp.json();
    const apiConfig = currentData.api_config || {};
    
    if (type === 'github') {
        apiConfig.github_token = document.getElementById('quick-github-token').value;
        apiConfig.github_repo = document.getElementById('quick-github-repo').value;
    } else if (type === 'postmark') {
        apiConfig.postmark_api_key = document.getElementById('quick-postmark-token').value;
        apiConfig.postmark_recipient_email = document.getElementById('quick-postmark-recipient').value;
    } else if (type === 'domain') {
        apiConfig.domain_name = document.getElementById('quick-domain-name').value;
        apiConfig.domain_verified = true;
    }
    
    const formData = new FormData();
    formData.append('api_config', JSON.stringify(apiConfig));
    try {
        const response = await apiFetch('/firm/settings', { method: 'POST', body: formData });
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('quickConnectModal')).hide();
            loadOnboarding();
        }
    } catch (e) { console.error(`Error saving ${type} settings`, e); }
}

async function loadReports() {
    try {
        const statsResp = await apiFetch('/reports/stats');
        const stats = await statsResp.json();
        document.getElementById('report-stat-leads').innerText = stats.total_leads;
        document.getElementById('report-stat-qualified').innerText = stats.qualified_leads;
        document.getElementById('report-stat-conv').innerText = stats.conversion_rate + '%';
        document.getElementById('report-stat-docs').innerText = stats.docs_analyzed;
        
        const table = document.getElementById('report-top-leads-table');
        table.innerHTML = stats.top_leads.map(lead => `
            <tr>
                <td class="ps-4">
                    <div class="fw-bold">${lead.full_name || 'Anonymous'}</div>
                    <div class="small text-muted">${new Date(lead.created_at).toLocaleDateString()}</div>
                </td>
                <td><span class="badge bg-light text-dark border">${lead.case_type || 'General'}</span></td>
                <td><div class="fw-bold text-primary">${lead.score || 0}</div></td>
                <td class="text-end pe-4"><button class="btn btn-sm btn-outline-primary rounded-pill" onclick="viewLead(${lead.id})">Details</button></td>
            </tr>
        `).join('') || '<tr><td colspan="4" class="text-center py-4 text-muted">No high-scoring leads this week.</td></tr>';

        const firmResp = await apiFetch('/firm/me');
        const firm = await firmResp.json();
        document.getElementById('report-recipient-email').value = firm.api_config?.report_recipient_email || firm.api_config?.postmark_recipient_email || '';
    } catch (e) { console.error("Error loading reports", e); }
}

async function triggerWeeklyReport() {
    const btn = event ? event.target.closest('button') : null;
    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Sending...'; }
    try {
        const response = await apiFetch('/reports/trigger', { method: 'POST' });
        const result = await response.json();
        if (result.status === 'success') alert(`Report sent successfully to ${result.recipient}!`);
        else alert(`Failed to send report: ${result.message || 'Unknown error'}`);
    } catch (e) { alert("Error triggering report."); } finally { if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-envelope-paper me-1"></i> Send Weekly Report Now'; } }
}

async function saveReportSettings() {
    const email = document.getElementById('report-recipient-email').value;
    if (!email) return alert("Please enter a recipient email.");
    const currentResp = await apiFetch('/firm/me');
    const currentData = await currentResp.json();
    const apiConfig = currentData.api_config || {};
    apiConfig.report_recipient_email = email;
    const formData = new FormData();
    formData.append('api_config', JSON.stringify(apiConfig));
    try {
        const response = await apiFetch('/firm/settings', { method: 'POST', body: formData });
        if (response.ok) alert("Report settings saved!");
    } catch (e) { console.error("Error saving report settings", e); }
}

async function loadIntegrations() {
    try {
        const response = await apiFetch('/firm/integrations');
        const integrations = await response.json();
        integrations.forEach(i => {
            if (i.crm_system === 'clio') {
                document.getElementById('clio-api-key').value = i.api_key || '';
                document.getElementById('clio-active-toggle').checked = i.is_active === 1;
                document.getElementById('clio-auto-sync-toggle').checked = i.auto_sync_enabled === 1;
            } else if (i.crm_system === 'filevine') {
                document.getElementById('filevine-api-key').value = i.api_key || '';
                document.getElementById('filevine-active-toggle').checked = i.is_active === 1;
                document.getElementById('filevine-auto-sync-toggle').checked = i.auto_sync_enabled === 1;
                try {
                    const cfg = JSON.parse(i.config_json);
                    document.getElementById('filevine-session-id').value = cfg.session_id || '';
                } catch(e) {}
            }
        });
    } catch (e) { console.error("Error loading integrations", e); }
}

async function saveIntegration(system) {
    const formData = new FormData();
    formData.append('crm_system', system);
    if (system === 'clio') {
        formData.append('api_key', document.getElementById('clio-api-key').value);
        formData.append('is_active', document.getElementById('clio-active-toggle').checked ? 1 : 0);
        formData.append('auto_sync_enabled', document.getElementById('clio-auto-sync-toggle').checked ? 1 : 0);
    } else if (system === 'filevine') {
        formData.append('api_key', document.getElementById('filevine-api-key').value);
        formData.append('is_active', document.getElementById('filevine-active-toggle').checked ? 1 : 0);
        formData.append('auto_sync_enabled', document.getElementById('filevine-auto-sync-toggle').checked ? 1 : 0);
        formData.append('config_json', JSON.stringify({ session_id: document.getElementById('filevine-session-id').value }));
    }
    try {
        const response = await apiFetch('/firm/integrations', { method: 'POST', body: formData });
        if (response.ok) alert(system.charAt(0).toUpperCase() + system.slice(1) + " integration saved!");
    } catch (e) { console.error("Error saving integration", e); }
}

async function updateIntegrationStatus(system) { saveIntegration(system); }

loadLeads();
setInterval(() => {
    if (!document.getElementById('filter-status').value && !document.getElementById('filter-score').value && !document.getElementById('search-input').value) loadLeads();
}, 30000);
