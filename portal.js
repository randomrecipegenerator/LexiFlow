// LexiFlow Client Portal Logic
// API_BASE is defined in config.js

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const filesContainer = document.getElementById('files-container');
const uploadBtn = document.getElementById('upload-btn');
const uploadContainer = document.getElementById('upload-container');
const successContainer = document.getElementById('success-container');

// State
let selectedFiles = [];
const urlParams = new URLSearchParams(window.location.search);
const leadId = urlParams.get('lead_id') || urlParams.get('id');

// Initialize
function init() {
    if (!leadId) {
        console.warn('No lead_id found in URL. Document association might fail.');
        // In a real app, we might redirect or show an error
    }

    // Drag and Drop listeners
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drop-zone--over');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('drop-zone--over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drop-zone--over');
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    uploadBtn.addEventListener('click', startUpload);
}

function handleFiles(files) {
    const newFiles = Array.from(files);
    selectedFiles = [...selectedFiles, ...newFiles];
    renderFileList();
}

function renderFileList() {
    if (selectedFiles.length > 0) {
        fileList.classList.remove('hidden');
        uploadBtn.disabled = false;
    } else {
        fileList.classList.add('hidden');
        uploadBtn.disabled = true;
    }

    filesContainer.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100';
        fileItem.innerHTML = `
            <div class="flex items-center gap-3">
                <i class="bi ${getFileIcon(file.name)} text-slate-400"></i>
                <div>
                    <div class="text-sm font-medium text-slate-700 truncate max-w-[200px]">${file.name}</div>
                    <div class="text-[10px] text-slate-400 uppercase tracking-tight">${(file.size / 1024).toFixed(1)} KB</div>
                </div>
            </div>
            <button onclick="removeFile(${index})" class="text-slate-300 hover:text-red-500 transition">
                <i class="bi bi-x-circle"></i>
            </button>
        `;
        filesContainer.appendChild(fileItem);
    });
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'pdf') return 'bi-file-earmark-pdf';
    if (['jpg', 'jpeg', 'png'].includes(ext)) return 'bi-file-earmark-image';
    return 'bi-file-earmark-text';
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
}

// Make removeFile global so the onclick works
window.removeFile = removeFile;

async function startUpload() {
    if (selectedFiles.length === 0) return;
    if (!leadId) {
        alert('Error: No Lead ID found. Please access the portal through the link provided by your attorney.');
        return;
    }

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat animate-spin"></i> Securing & Uploading...`;

    try {
        // Upload files one by one or in parallel
        const uploadPromises = selectedFiles.map(file => {
            const formData = new FormData();
            formData.append('file', file);
            
            // Note: The existing backend endpoint is /chat/upload?lead_id=...
            // But main.py defines it as @app.post("/chat/upload") with lead_id as a param
            // In FastAPI, if it's not in the path or body, it's a query param
            return apiFetch(`/chat/upload?lead_id=${leadId}`, {
                method: 'POST',
                body: formData
            });
        });

        await Promise.all(uploadPromises);
        
        // Show success
        uploadContainer.classList.add('hidden');
        successContainer.classList.remove('hidden');
        
    } catch (err) {
        console.error('Upload error:', err);
        alert('There was an error uploading your documents. Please try again or contact support.');
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<i class="bi bi-shield-check"></i> Start Secure Analysis`;
    }
}

init();
