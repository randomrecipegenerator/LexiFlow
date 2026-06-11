/**
 * LexiFlow Desktop — Electron Main Process
 * 
 * Handles:
 * - Window management & native menus
 * - Directory picking via electron.dialog
 * - IPC bridge for sync engine & redaction
 * - Cloud API communication
 * - Auto-updater (future)
 */
const { app, BrowserWindow, ipcMain, dialog, Menu, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { SyncEngine } = require('./sync-engine');
const { RedactUtils } = require('./redact-utils');

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
}

let mainWindow = null;
let syncEngine = null;
let redactUtils = null;

const CLOUD_API_BASE = process.env.LEXIFLOW_API_URL || 'https://lexiflow.co/api/desktop';
const DEFAULT_SYNC_INTERVAL = 300; // 5 seconds in dev, 300 in production

// =========================================================================
// Window Creation
// =========================================================================

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        title: 'LexiFlow Desktop',
        icon: path.join(__dirname, 'assets', 'icon.png'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: false,
        },
    });

    // In development, load from local dev server; in production, load bundled UI
    const isDev = process.env.ELECTRON_DEV === 'true';
    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
    }

    // Build the application menu
    const menuTemplate = [
        {
            label: 'LexiFlow',
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'quit' },
            ],
        },
        {
            label: 'File',
            submenu: [
                {
                    label: 'Add Sync Folder...',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => handlePickFolder(),
                },
                { type: 'separator' },
                { role: 'close' },
            ],
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' },
            ],
        },
    ];
    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate));
}

// =========================================================================
// Directory Picker
// =========================================================================

async function handlePickFolder() {
    if (!mainWindow) return;

    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        title: 'Select a folder to sync with Discovery-Vault',
    });

    if (result.canceled || result.filePaths.length === 0) return;

    const folderPath = result.filePaths[0];
    const folderName = path.basename(folderPath);

    // Register with cloud API
    try {
        const apiKey = await getApiKey();
        const response = await fetch(`${CLOUD_API_BASE}/folders/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
            },
            body: JSON.stringify({
                local_path: folderPath,
                label: folderName,
                watch_subfolders: true,
                file_extensions: ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.docx', '.txt'],
            }),
        });

        const data = await response.json();

        // Start watching this folder via the sync engine
        if (syncEngine) {
            syncEngine.watchFolder(data.folder_id, folderPath);
        }

        mainWindow.webContents.send('folder-registered', {
            folder_id: data.folder_id,
            local_path: folderPath,
            label: folderName,
        });
    } catch (err) {
        mainWindow.webContents.send('folder-error', {
            error: err.message,
            local_path: folderPath,
        });
    }
}

// =========================================================================
// API Key Management
// =========================================================================

async function getApiKey() {
    const store = require('electron-store');
    const config = new store({ name: 'lexiflow-config' });
    let apiKey = config.get('apiKey');

    if (!apiKey) {
        // Register this device with the cloud
        const deviceId = require('crypto').randomUUID();
        const response = await fetch(`${CLOUD_API_BASE}/auth/register-client`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                device_name: `LexiFlow Desktop - ${require('os').hostname()}`,
                device_id: deviceId,
                os_info: `${require('os').platform()} ${require('os').release()}`,
            }),
        });

        const data = await response.json();
        apiKey = data.api_key;
        config.set('apiKey', apiKey);
        config.set('clientId', data.client_id);
    }

    return apiKey;
}

// =========================================================================
// IPC Handlers
// =========================================================================

function registerIpcHandlers() {
    // -- Folder Operations --

    ipcMain.handle('pick-folder', async () => {
        await handlePickFolder();
        return true;
    });

    ipcMain.handle('get-folders', async () => {
        const apiKey = await getApiKey();
        const response = await fetch(`${CLOUD_API_BASE}/folders`, {
            headers: { 'X-API-Key': apiKey },
        });
        return response.json();
    });

    ipcMain.handle('remove-folder', async (event, folderId) => {
        if (syncEngine) syncEngine.unwatchFolder(folderId);
        return { status: 'removed', folder_id: folderId };
    });

    // -- Redaction Operations --

    ipcMain.handle('redact-document', async (event, filePath) => {
        if (!redactUtils) redactUtils = new RedactUtils();
        
        const result = await redactUtils.redactFile(filePath);
        
        // Notify cloud that redaction was completed
        const apiKey = await getApiKey();
        await fetch(`${CLOUD_API_BASE}/redact/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
            },
            body: JSON.stringify({
                document_id: path.basename(filePath),
                redacted_file_path: result.outputPath,
                redacted_fields_count: result.redactedCount,
                redaction_log: result.log,
            }),
        });

        return result;
    });

    ipcMain.handle('scan-file-for-pii', async (event, filePath) => {
        if (!redactUtils) redactUtils = new RedactUtils();
        return redactUtils.scanFile(filePath);
    });

    // -- Sync Operations --

    ipcMain.handle('start-sync', async () => {
        if (syncEngine) syncEngine.start();
        return { status: 'sync_started' };
    });

    ipcMain.handle('stop-sync', async () => {
        if (syncEngine) syncEngine.stop();
        return { status: 'sync_stopped' };
    });

    ipcMain.handle('get-sync-status', async () => {
        if (syncEngine) return syncEngine.getStatus();
        return { status: 'not_initialized' };
    });

    ipcMain.handle('sync-now', async () => {
        if (syncEngine) await syncEngine.syncAll();
        return { status: 'sync_completed' };
    });

    // -- Health Check --

    ipcMain.handle('check-cloud-connection', async () => {
        try {
            const response = await fetch(`${CLOUD_API_BASE}/health`);
            const data = await response.json();
            return { connected: true, data };
        } catch (err) {
            return { connected: false, error: err.message };
        }
    });
}

// =========================================================================
// App Lifecycle
// =========================================================================

app.whenReady().then(async () => {
    createWindow();
    registerIpcHandlers();

    // Initialize sync engine
    syncEngine = new SyncEngine({
        apiBase: CLOUD_API_BASE,
        getApiKey,
        syncInterval: process.env.ELECTRON_DEV ? 5 : DEFAULT_SYNC_INTERVAL,
    });

    // Initialize redact utils
    redactUtils = new RedactUtils();

    // Start sync engine automatically
    syncEngine.start();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (syncEngine) syncEngine.stop();
    if (process.platform !== 'darwin') app.quit();
});

// Handle second instances
app.on('second-instance', () => {
    if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.focus();
    }
});