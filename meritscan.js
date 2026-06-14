// MeritScan Application Logic
// API_BASE is defined in config.js

// DOM Elements
const uploadBtn = document.getElementById('upload-btn');
const uploadModal = document.getElementById('upload-modal');
const cancelUpload = document.getElementById('cancel-upload');
const confirmUpload = document.getElementById('confirm-upload');
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const fileInfo = document.getElementById('file-info');
const filenameDisplay = document.getElementById('filename-display');
const recordGrid = document.getElementById('record-grid');
const recordListSection = document.getElementById('record-list-section');
const resultSection = document.getElementById('result-section');
const backToList = document.getElementById('back-to-list');

// State
let selectedFile = null;

// Initialize
function init() {
    loadRecords();
    
    if (uploadBtn) uploadBtn.onclick = () => uploadModal.classList.remove('hidden');
    if (cancelUpload) cancelUpload.onclick = () => {
        uploadModal.classList.add('hidden');
        resetUpload();
    };
    
    if (dropZone) dropZone.onclick = () => fileInput.click();
    if (fileInput) fileInput.onchange = (e) => handleFileSelection(e.target.files[0]);
    
    if (dropZone) {
        dropZone.ondragover = (e) => {
            e.preventDefault();
            dropZone.classList.add('border-blue-500', 'bg-blue-50');
        };
        dropZone.ondragleave = () => {
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        };
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
            handleFileSelection(e.dataTransfer.files[0]);
        };
    }
    
    if (confirmUpload) confirmUpload.onclick = startUpload;
    
    if (backToList) backToList.onclick = () => {
        resultSection.classList.add('hidden');
        recordListSection.classList.remove('hidden');
    };
}

function handleFileSelection(file) {
    if (!file) return;
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

async function startUpload() {
    if (!selectedFile) return;

    confirmUpload.disabled = true;
    confirmUpload.innerText = 'Uploading...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const res = await apiFetch('/meritscan/upload', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) throw new Error(`Upload failed with status ${res.status}`);

        const data = await res.json();
        console.log('Upload Success:', data);

        if (uploadModal) uploadModal.classList.add('hidden');
        resetUpload();
        if (confirmUpload) confirmUpload.innerText = 'Start Analysis';
        loadRecords();
    } catch (err) {
        console.error('Upload Error:', err);
        alert('Upload failed: ' + err.message);
        if (confirmUpload) {
            confirmUpload.disabled = false;
            confirmUpload.innerText = 'Start Analysis';
        }
    }
}

async function loadRecords() {
    if (!recordGrid) return;
    try {
        const res = await apiFetch('/meritscan/reports');
        if (!res.ok) throw new Error(`Failed to load records: ${res.status}`);

        const records = await res.json();
        if (!Array.isArray(records)) {
            console.error('Expected records array, got:', records);
            return;
        }

        recordGrid.innerHTML = '';
        if (records.length === 0) {
            recordGrid.innerHTML = '<div class="col-span-full text-center py-12 text-gray-500">No medical records uploaded yet.</div>';
            return;
        }

        records.forEach(r => {
            if (!r) return;
            const card = document.createElement('div');
            card.className = 'bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer';
            card.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div class="p-3 bg-blue-100 text-blue-600 rounded-lg">
                        <i class="fas fa-file-medical text-xl"></i>
                    </div>
                    <span class="text-xs font-bold uppercase px-2 py-1 rounded ${getStatusClass(r.status)}">${r.status || 'unknown'}</span>
                </div>
                <h3 class="font-bold text-lg mb-1 truncate" title="${r.filename || 'Untitled'}">${r.filename || 'Untitled'}</h3>
                <p class="text-gray-500 text-sm mb-4">${r.upload_date ? new Date(r.upload_date).toLocaleDateString() : 'N/A'}</p>
                <div class="flex justify-end">
                    <button class="text-blue-600 font-semibold text-sm hover:underline" onclick="event.stopPropagation(); viewResult(${r.id})">View Report →</button>
                </div>
            `;
            card.onclick = () => viewResult(r.id);
            recordGrid.appendChild(card);
        });
    } catch (err) {
        console.error('Load Records Error:', err);
    }
}

async function viewResult(id) {
    if (!id) return;
    try {
        const res = await apiFetch(`/meritscan/reports/${id}`);
        if (!res.ok) throw new Error(`Failed to load report: ${res.status}`);

        const data = await res.json();
        if (!data || !data.record) throw new Error('Invalid report data received');

        if (data.record.status !== 'completed') {
            alert('Analysis still in progress or failed. Status: ' + (data.record.status || 'unknown'));
            return;
        }

        if (recordListSection) recordListSection.classList.add('hidden');
        if (resultSection) resultSection.classList.remove('hidden');

        // Populate Result
        const summaryEl = document.getElementById('summary-text');
        if (summaryEl) summaryEl.innerText = data.report?.executive_summary || 'No summary available.';

        const chronologyEl = document.getElementById('chronology-text');
        if (chronologyEl) chronologyEl.innerText = data.report?.chronology || 'No chronology available.';

        const negligenceEl = document.getElementById('negligence-text');
        if (negligenceEl) negligenceEl.innerText = data.report?.negligence_markers || 'No negligence markers identified.';

        const socEl = document.getElementById('soc-text');
        if (socEl) socEl.innerText = data.report?.standard_of_care_analysis || 'No standard of care analysis available.';

    } catch (err) {
        console.error('View Result Error:', err);
        alert('Failed to load results: ' + err.message);
    }
}

init();
setInterval(loadRecords, 5000);
