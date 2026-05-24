let allForms = [];
let fbQuestions = [];

function showSection(section) {
    document.getElementById('section-leads').classList.add('d-none');
    document.getElementById('section-forms').classList.add('d-none');
    document.getElementById('section-billing').classList.add('d-none');
    document.getElementById('nav-leads').classList.remove('active');
    document.getElementById('nav-forms').classList.remove('active');
    document.getElementById('nav-billing').classList.remove('active');

    if (section === 'leads') {
        document.getElementById('section-leads').classList.remove('d-none');
        document.getElementById('nav-leads').classList.add('active');
    } else if (section === 'forms') {
        document.getElementById('section-forms').classList.remove('d-none');
        document.getElementById('nav-forms').classList.add('active');
        loadForms();
    } else if (section === 'billing') {
        document.getElementById('section-billing').classList.remove('d-none');
        document.getElementById('nav-billing').classList.add('active');
        loadInvoices();
    }
}


async function loadForms() {
    try {
        const response = await fetch(API_BASE + '/forms');
        allForms = await response.json();
        renderFormsList();
    } catch (e) {
        console.error("Error loading forms", e);
    }
}

function renderFormsList() {
    const container = document.getElementById('forms-list');
    container.innerHTML = '';
    
    if (allForms.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-file-earmark-plus display-1 text-light"></i>
                <h4 class="text-muted mt-3">No intake forms yet</h4>
                <p class="text-muted">Create your first dynamic form to start capturing leads.</p>
            </div>
        `;
        return;
    }

    allForms.forEach(form => {
        const publicUrl = `${window.location.origin}/form_view.html?id=${form.id}`;
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-4';
        card.innerHTML = `
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <h5 class="card-title fw-bold mb-0">${form.name}</h5>
                        <span class="badge bg-primary-subtle text-primary">Active</span>
                    </div>
                    <p class="text-muted small">Created on ${new Date(form.created_at).toLocaleDateString()}</p>
                    <div class="input-group input-group-sm mb-3">
                        <input type="text" class="form-control bg-light border-0" value="${publicUrl}" readonly>
                        <button class="btn btn-outline-secondary" onclick="copyToClipboard('${publicUrl}')">
                            <i class="bi bi-copy"></i>
                        </button>
                    </div>
                </div>
                <div class="card-footer bg-white border-top-0 pb-3">
                    <div class="d-flex gap-2">
                        <a href="${publicUrl}" target="_blank" class="btn btn-sm btn-primary flex-grow-1">View Form</a>
                        <button class="btn btn-sm btn-outline-danger" onclick="alert('Delete placeholder')"><i class="bi bi-trash"></i></button>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert("URL copied to clipboard!");
    });
}

function openFormBuilder() {
    fbQuestions = [];
    document.getElementById('fb-name').value = '';
    document.getElementById('fb-logo').value = '';
    document.getElementById('fb-color').value = '#0d6efd';
    document.getElementById('fb-questions-container').innerHTML = '';
    
    // Add a default name question
    addFBQuestion('What is your full name?', 'text');
    
    const modal = new bootstrap.Modal(document.getElementById('formBuilderModal'));
    modal.show();
}

function addFBQuestion(text = '', type = 'text') {
    const id = Date.now();
    fbQuestions.push({ id, text, type, logic: null });
    renderFBQuestions();
}

function renderFBQuestions() {
    const container = document.getElementById('fb-questions-container');
    container.innerHTML = '';
    
    fbQuestions.forEach((q, index) => {
        const qDiv = document.createElement('div');
        qDiv.className = 'card mb-3 border-0 bg-light';
        qDiv.innerHTML = `
            <div class="card-body p-3">
                <div class="d-flex justify-content-between mb-2">
                    <span class="badge bg-secondary">Question ${index + 1}</span>
                    <button class="btn btn-sm text-danger" onclick="removeFBQuestion(${q.id})"><i class="bi bi-trash"></i></button>
                </div>
                <div class="mb-2">
                    <input type="text" class="form-control form-control-sm" placeholder="Enter question text" 
                        value="${q.text}" onchange="updateFBQuestion(${q.id}, 'text', this.value)">
                </div>
                <div class="row g-2">
                    <div class="col-md-6">
                        <select class="form-select form-select-sm" onchange="updateFBQuestion(${q.id}, 'type', this.value)">
                            <option value="text" ${q.type === 'text' ? 'selected' : ''}>Text Input</option>
                            <option value="date" ${q.type === 'date' ? 'selected' : ''}>Date</option>
                            <option value="yes_no" ${q.type === 'yes_no' ? 'selected' : ''}>Yes / No</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <button class="btn btn-sm btn-outline-secondary w-100" onclick="toggleFBLogic(${q.id})">
                            <i class="bi bi-diagram-2"></i> ${q.logic ? 'Logic Set' : 'Add Logic'}
                        </button>
                    </div>
                </div>
                ${q.showLogic ? renderFBLogicEditor(q) : ''}
            </div>
        `;
        container.appendChild(qDiv);
    });
}

function removeFBQuestion(id) {
    fbQuestions = fbQuestions.filter(q => q.id !== id);
    renderFBQuestions();
}

function updateFBQuestion(id, field, value) {
    const q = fbQuestions.find(q => q.id === id);
    if (q) q[field] = value;
}

function toggleFBLogic(id) {
    const q = fbQuestions.find(q => q.id === id);
    if (q) {
        q.showLogic = !q.showLogic;
        renderFBQuestions();
    }
}

function renderFBLogicEditor(q) {
    // Simple logic: Only show this question if a PREVIOUS question has a certain value
    // For this prototype, let's just support "Show if Question X is Yes/No"
    const prevQuestions = fbQuestions.filter(prev => fbQuestions.indexOf(prev) < fbQuestions.indexOf(q));
    
    if (prevQuestions.length === 0) {
        return `<div class="mt-2 small text-muted italic">Logic can only depend on previous questions.</div>`;
    }

    return `
        <div class="mt-3 p-2 border-top">
            <label class="small fw-bold">Conditional Logic</label>
            <div class="row g-2 align-items-center mt-1">
                <div class="col-12 small mb-1">Show this question ONLY if:</div>
                <div class="col-md-5">
                    <select class="form-select form-select-sm" id="logic-dep-${q.id}">
                        ${prevQuestions.map(p => `<option value="${p.id}" ${q.logic?.dependsOn === p.id ? 'selected' : ''}>Q: ${p.text.substring(0, 20)}...</option>`).join('')}
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select form-select-sm" id="logic-val-${q.id}">
                        <option value="Yes" ${q.logic?.value === 'Yes' ? 'selected' : ''}>is Yes</option>
                        <option value="No" ${q.logic?.value === 'No' ? 'selected' : ''}>is No</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <button class="btn btn-sm btn-primary w-100" onclick="saveFBLogic(${q.id})">Set Logic</button>
                </div>
            </div>
        </div>
    `;
}

function saveFBLogic(id) {
    const depId = document.getElementById(`logic-dep-${id}`).value;
    const val = document.getElementById(`logic-val-${id}`).value;
    const q = fbQuestions.find(q => q.id === id);
    if (q) {
        q.logic = { dependsOn: parseInt(depId), value: val };
        q.showLogic = false;
        renderFBQuestions();
    }
}

async function saveForm() {
    const name = document.getElementById('fb-name').value;
    if (!name) return alert("Please enter a form name");
    
    const branding = {
        logo: document.getElementById('fb-logo').value,
        color: document.getElementById('fb-color').value
    };
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('branding_logo', branding.logo);
    formData.append('branding_colors', branding.color);
    formData.append('questions_json', JSON.stringify(fbQuestions));
    
    try {
        const response = await fetch(API_BASE + '/forms', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.form_id) {
            bootstrap.Modal.getInstance(document.getElementById('formBuilderModal')).hide();
            loadForms();
        }
    } catch (e) {
        console.error("Save failed", e);
    }
}
