// API_BASE is defined in config.js
const DEPO_API_PREFIX = '/depolens';

// DOM Elements
const uploadBtn = document.getElementById('upload-btn');
const uploadModal = document.getElementById('upload-modal');
const cancelUpload = document.getElementById('cancel-upload');
const confirmUpload = document.getElementById('confirm-upload');
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const fileInfo = document.getElementById('file-info');
const filenameDisplay = document.getElementById('filename-display');
const transcriptGrid = document.getElementById('transcript-grid');
const transcriptListSection = document.getElementById('transcript-list-section');
const resultSection = document.getElementById('result-section');
const backToList = document.getElementById('back-to-list');

// State
let selectedFile = null;

// Initialize
async function init() {
    loadTranscripts();
}

// Event Listeners
if (uploadBtn) uploadBtn.addEventListener('click', () => uploadModal.classList.remove('hidden'));
if (cancelUpload) cancelUpload.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
    resetUpload();
});

if (dropZone) dropZone.addEventListener('click', () => fileInput.click());
if (fileInput) fileInput.addEventListener('change', handleFileSelect);

if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-blue-500');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
}

if (confirmUpload) confirmUpload.addEventListener('click', uploadTranscript);
if (backToList) backToList.addEventListener('click', () => {
    resultSection.classList.add('hidden');
    transcriptListSection.classList.remove('hidden');
    loadTranscripts();
});

function handleFileSelect(e) {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    selectedFile = file;
    if (filenameDisplay) filenameDisplay.innerText = file.name;
    if (fileInfo) fileInfo.classList.remove('hidden');
    if (confirmUpload) confirmUpload.disabled = false;
}

function resetUpload() {
    selectedFile = null;
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.classList.add('hidden');
    if (confirmUpload) confirmUpload.disabled = true;
}

async function uploadTranscript() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    if (confirmUpload) {
        confirmUpload.innerText = 'Uploading...';
        confirmUpload.disabled = true;
    }

    try {
        const res = await apiFetch(`${DEPO_API_PREFIX}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) throw new Error(`Upload failed with status ${res.status}`);

        const data = await res.json();
        console.log('Upload Response:', data);

        if (uploadModal) uploadModal.classList.add('hidden');
        resetUpload();
        if (confirmUpload) confirmUpload.innerText = 'Start Analysis';
        loadTranscripts();
    } catch (err) {
        console.error('Upload Error:', err);
        alert('Upload failed: ' + err.message);
        if (confirmUpload) {
            confirmUpload.innerText = 'Start Analysis';
            confirmUpload.disabled = false;
        }
    }
}

async function loadTranscripts() {
    if (!transcriptGrid) return;
    try {
        const res = await apiFetch(`${DEPO_API_PREFIX}/transcripts`);
        if (!res.ok) throw new Error(`Failed to load transcripts: ${res.status}`);

        const transcripts = await res.json();
        if (!Array.isArray(transcripts)) {
            console.error('Expected transcripts array, got:', transcripts);
            return;
        }

        transcriptGrid.innerHTML = '';
        if (transcripts.length === 0) {
            transcriptGrid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--text-muted);"><i class="bi bi-file-text" style="font-size:3rem;display:block;margin-bottom:12px;"></i><p>No transcripts found.</p></div>';
            return;
        }

        transcripts.forEach(t => {
            if (!t) return;
            const card = document.createElement('div');
            card.className = 'bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer';
            card.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div class="p-3 bg-blue-100 text-blue-600 rounded-lg">
                        <i class="fas fa-file-alt text-xl"></i>
                    </div>
                    <span class="text-xs font-bold uppercase px-2 py-1 rounded ${getStatusClass(t.status)}">${t.status || 'unknown'}</span>
                </div>
                <h3 class="font-bold text-lg mb-1 truncate" title="${t.filename || 'Untitled'}">${t.filename || 'Untitled'}</h3>
                <p class="text-gray-500 text-sm mb-4">${t.upload_date ? new Date(t.upload_date).toLocaleDateString() : 'N/A'}</p>
                <div class="flex justify-end">
                    <button class="text-blue-600 font-semibold text-sm hover:underline" onclick="event.stopPropagation(); viewResult(${t.id})">View Analysis →</button>
                </div>
            `;
            card.onclick = () => viewResult(t.id);
            transcriptGrid.appendChild(card);
        });
    } catch (err) {
        console.error('Load Transcripts Error:', err);
    }
}

async function viewResult(id) {
    if (!id) return;
    try {
        const res = await apiFetch(`${DEPO_API_PREFIX}/transcripts/${id}`);
        if (!res.ok) throw new Error(`Failed to load result: ${res.status}`);

        const data = await res.json();
        if (!data || !data.transcript) throw new Error('Invalid data structure returned');

        if (data.transcript.status !== 'completed') {
            alert('Analysis still in progress or failed. Status: ' + (data.transcript.status || 'unknown'));
            return;
        }

        if (transcriptListSection) transcriptListSection.classList.add('hidden');
        if (resultSection) resultSection.classList.remove('hidden');

        // Populate Summary
        const summaryEl = document.getElementById('summary-text');
        if (summaryEl) summaryEl.innerText = data.summary?.executive_summary || 'No summary available.';

        const risksList = document.getElementById('risks-list');
        if (risksList) risksList.innerHTML = (data.summary?.risks || '').split('\n').filter(r => r.trim()).map(r => `<li>${r}</li>`).join('') || '<li>No risks identified.</li>';

        const admissionsList = document.getElementById('admissions-list');
        if (admissionsList) admissionsList.innerHTML = (data.summary?.admissions || '').split('\n').filter(a => a.trim()).map(a => `<li>${a}</li>`).join('') || '<li>No admissions found.</li>';

        // Populate Conflicts
        const conflictCountEl = document.getElementById('conflict-count');
        const conflicts = Array.isArray(data.conflicts) ? data.conflicts : [];
        if (conflictCountEl) conflictCountEl.innerText = `${conflicts.length} Conflicts`;

        const conflictsContainer = document.getElementById('conflicts-container');
        if (conflictsContainer) {
            if (conflicts.length === 0) {
                conflictsContainer.innerHTML = '<p class="text-sm text-gray-500 italic">No direct conflicts detected.</p>';
            } else {
                conflictsContainer.innerHTML = conflicts.map(c => `
                    <div class="p-4 border border-red-100 bg-red-50 rounded-lg">
                        <div class="flex justify-between items-start mb-2">
                            <h4 class="font-bold text-red-800">${c.witness_a || 'Witness A'} vs ${c.witness_b || 'Witness B'}</h4>
                            <span class="text-xs font-bold px-2 py-1 rounded bg-red-200 text-red-900">${c.severity || 'Medium'}</span>
                        </div>
                        <p class="text-sm text-gray-800 mb-2 font-medium">${c.description || 'Conflict detected in testimony.'}</p>
                        <div class="text-xs text-gray-600 bg-white p-2 rounded border border-red-50">
                            <strong>Reasoning:</strong> ${c.reasoning || 'N/A'}
                        </div>
                    </div>
                `).join('');
            }
        }

        // Populate Chronology
        const chronologyBody = document.getElementById('chronology-body');
        const facts = Array.isArray(data.facts) ? data.facts : [];
        if (chronologyBody) {
            if (facts.length === 0) {
                chronologyBody.innerHTML = '<tr><td colspan="4" class="px-4 py-8 text-center text-gray-500 italic">No facts extracted.</td></tr>';
            } else {
                chronologyBody.innerHTML = facts.map(f => `
                    <tr>
                        <td class="px-4 py-3 text-sm font-medium text-gray-900">${f.witness_name || 'Unknown'}</td>
                        <td class="px-4 py-3 text-sm text-gray-500">${f.date_time || 'N/A'}</td>
                        <td class="px-4 py-3 text-sm text-gray-700">${f.event_description || 'N/A'}</td>
                        <td class="px-4 py-3 text-sm text-gray-500 italic">p.${f.page_reference || '?'}</td>
                    </tr>
                `).join('');
            }
        }

    } catch (err) {
        console.error('View Result Error:', err);
        alert('Failed to load results: ' + err.message);
    }
}

init();
setInterval(loadTranscripts, 10000); // Polling for updates
