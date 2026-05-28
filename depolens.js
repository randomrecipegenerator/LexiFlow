const API_BASE = '/api/depolens'; // Using a proxy or relative path

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
uploadBtn.addEventListener('click', () => uploadModal.classList.remove('hidden'));
cancelUpload.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
    resetUpload();
});

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);

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

confirmUpload.addEventListener('click', uploadTranscript);
backToList.addEventListener('click', () => {
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
    filenameDisplay.innerText = file.name;
    fileInfo.classList.remove('hidden');
    confirmUpload.disabled = false;
}

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    confirmUpload.disabled = true;
}

async function uploadTranscript() {
    const formData = new FormData();
    formData.append('file', selectedFile);

    confirmUpload.innerText = 'Uploading...';
    confirmUpload.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        uploadModal.classList.add('hidden');
        resetUpload();
        confirmUpload.innerText = 'Start Analysis';
        loadTranscripts();
    } catch (err) {
        console.error(err);
        alert('Upload failed');
        confirmUpload.innerText = 'Start Analysis';
        confirmUpload.disabled = false;
    }
}

async function loadTranscripts() {
    try {
        const res = await fetch(`${API_BASE}/transcripts`);
        const transcripts = await res.json();
        
        transcriptGrid.innerHTML = '';
        transcripts.forEach(t => {
            const card = document.createElement('div');
            card.className = 'bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer';
            card.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div class="p-3 bg-blue-100 text-blue-600 rounded-lg">
                        <i class="fas fa-file-alt text-xl"></i>
                    </div>
                    <span class="text-xs font-bold uppercase px-2 py-1 rounded ${getStatusClass(t.status)}">${t.status}</span>
                </div>
                <h3 class="font-bold text-lg mb-1 truncate" title="${t.filename}">${t.filename}</h3>
                <p class="text-gray-500 text-sm mb-4">${new Date(t.upload_date).toLocaleDateString()}</p>
                <div class="flex justify-end">
                    <button class="text-blue-600 font-semibold text-sm hover:underline" onclick="viewResult(${t.id})">View Analysis →</button>
                </div>
            `;
            card.onclick = () => viewResult(t.id);
            transcriptGrid.appendChild(card);
        });
    } catch (err) {
        console.error(err);
    }
}

function getStatusClass(status) {
    switch (status) {
        case 'completed': return 'bg-green-100 text-green-700';
        case 'processing': return 'bg-yellow-100 text-yellow-700';
        case 'error': return 'bg-red-100 text-red-700';
        default: return 'bg-gray-100 text-gray-700';
    }
}

async function viewResult(id) {
    try {
        const res = await fetch(`${API_BASE}/transcripts/${id}`);
        const data = await res.json();
        
        if (data.transcript.status !== 'completed') {
            alert('Analysis still in progress or failed. Status: ' + data.transcript.status);
            return;
        }

        transcriptListSection.classList.add('hidden');
        resultSection.classList.remove('hidden');

        // Populate Summary
        document.getElementById('summary-text').innerText = data.summary?.executive_summary || 'No summary available.';
        
        const risksList = document.getElementById('risks-list');
        risksList.innerHTML = (data.summary?.risks || '').split('\n').map(r => `<li>${r}</li>`).join('');
        
        const admissionsList = document.getElementById('admissions-list');
        admissionsList.innerHTML = (data.summary?.admissions || '').split('\n').map(a => `<li>${a}</li>`).join('');

        // Populate Conflicts
        document.getElementById('conflict-count').innerText = `${data.conflicts.length} Conflicts`;
        const conflictsContainer = document.getElementById('conflicts-container');
        conflictsContainer.innerHTML = data.conflicts.map(c => `
            <div class="p-4 border border-red-100 bg-red-50 rounded-lg">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="font-bold text-red-800">${c.witness_a} vs ${c.witness_b}</h4>
                    <span class="text-xs font-bold px-2 py-1 rounded bg-red-200 text-red-900">${c.severity}</span>
                </div>
                <p class="text-sm text-gray-800 mb-2 font-medium">${c.description}</p>
                <div class="text-xs text-gray-600 bg-white p-2 rounded border border-red-50">
                    <strong>Reasoning:</strong> ${c.reasoning}
                </div>
            </div>
        `).join('');

        // Populate Chronology
        const chronologyBody = document.getElementById('chronology-body');
        chronologyBody.innerHTML = data.facts.map(f => `
            <tr>
                <td class="px-4 py-3 text-sm font-medium text-gray-900">${f.witness_name}</td>
                <td class="px-4 py-3 text-sm text-gray-500">${f.date_time}</td>
                <td class="px-4 py-3 text-sm text-gray-700">${f.event_description}</td>
                <td class="px-4 py-3 text-sm text-gray-500 italic">p.${f.page_reference}</td>
            </tr>
        `).join('');

    } catch (err) {
        console.error(err);
        alert('Failed to load results');
    }
}

init();
setInterval(loadTranscripts, 10000); // Polling for updates
