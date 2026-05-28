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
        const data = await res.json();
        uploadModal.classList.add('hidden');
        resetUpload();
        confirmUpload.innerText = 'Start Analysis';
        loadRecords();
    } catch (err) {
        console.error(err);
        alert('Upload failed');
        confirmUpload.disabled = false;
        confirmUpload.innerText = 'Start Analysis';
    }
}

async function loadRecords() {
    if (!recordGrid) return;
    try {
        const res = await apiFetch('/meritscan/reports');
        const records = await res.json();
        recordGrid.innerHTML = '';
        
        if (records.length === 0) {
            recordGrid.innerHTML = '<div class="col-span-full text-center py-12 text-gray-500">No medical records uploaded yet.</div>';
            return;
        }

        records.forEach(r => {
            const card = document.createElement('div');
            card.className = 'bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer';
            card.innerHTML = `
                <div class="flex justify-between items-start mb-4">
                    <div class="p-3 bg-blue-100 text-blue-600 rounded-lg">
                        <i class="fas fa-file-medical text-xl"></i>
                    </div>
                    <span class="text-xs font-bold uppercase px-2 py-1 rounded ${getStatusClass(r.status)}">${r.status}</span>
                </div>
                <h3 class="font-bold text-lg mb-1 truncate" title="${r.filename}">${r.filename}</h3>
                <p class="text-gray-500 text-sm mb-4">${new Date(r.upload_date).toLocaleDateString()}</p>
                <div class="flex justify-end">
                    <button class="text-blue-600 font-semibold text-sm hover:underline" onclick="event.stopPropagation(); viewResult(${r.id})">View Report →</button>
                </div>
            `;
            card.onclick = () => viewResult(r.id);
            recordGrid.appendChild(card);
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
        const res = await apiFetch(`/meritscan/reports/${id}`);
        const data = await res.json();
        
        if (data.record.status !== 'completed') {
            alert('Analysis still in progress or failed. Status: ' + data.record.status);
            return;
        }
        
        recordListSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        
        // Populate Result
        document.getElementById('summary-text').innerText = data.report?.executive_summary || 'No summary available.';
        document.getElementById('chronology-text').innerText = data.report?.chronology || 'No chronology available.';
        document.getElementById('negligence-text').innerText = data.report?.negligence_markers || 'No negligence markers identified.';
        document.getElementById('soc-text').innerText = data.report?.standard_of_care_analysis || 'No standard of care analysis available.';
        
    } catch (err) {
        console.error(err);
        alert('Failed to load results');
    }
}

init();
setInterval(loadRecords, 5000);
