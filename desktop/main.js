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
const Store = require('electron-store');
const { SyncEngine } = require('./sync-engine');
const { RedactUtils } = require('./redact-utils');
const { createTray, updateTrayMenu } = require('./tray');

const config = new Store({ name: 'lexiflow-config' });

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

    mainWindow.on('close', (event) => {
        const minimizeToTray = config.get('minimizeToTray') !== false; // Default to true
        if (!app.isQuitting && minimizeToTray) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    // In development, load from local dev server; in production, load bundled UI
    const isDev = process.env.ELECTRON_DEV === 'true';
    const apiKey = config.get('apiKey');

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        if (apiKey) {
            mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
        } else {
            mainWindow.loadFile(path.join(__dirname, 'renderer', 'login.html'));
        }
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
    return config.get('apiKey');
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
        try {
            const apiKey = await getApiKey();
            if (!apiKey) {
                return { folders: [], total: 0, error: 'API key not configured' };
            }
            const response = await fetch(`${CLOUD_API_BASE}/folders`, {
                headers: { 'X-API-Key': apiKey },
            });
            if (!response.ok) {
                return { folders: [], total: 0, error: `Cloud API error: ${response.status}` };
            }
            return response.json();
        } catch (err) {
            return { folders: [], total: 0, error: err.message };
        }
    });

    ipcMain.handle('get-api-key', async () => {
        return config.get('apiKey');
    });

    ipcMain.handle('set-api-key', async (event, apiKey) => {
        if (apiKey) {
            config.set('apiKey', apiKey);
            return { status: 'saved' };
        } else {
            config.delete('apiKey');
            return { status: 'cleared' };
        }
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

    // -- SSO for Cloud Dashboard --

    ipcMain.handle('get-sso-token', async () => {
        try {
            const apiKey = await getApiKey();
            if (!apiKey) {
                return { token: null, error: 'API key not configured' };
            }
            const response = await fetch(`${CLOUD_API_BASE}/auth/sso-token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey,
                },
                body: JSON.stringify({
                    device_id: config.get('clientId'),
                    redirect_to: '/dashboard',
                }),
            });
            if (!response.ok) {
                return { token: null, error: `SSO error: ${response.status}` };
            }
            const data = await response.json();
            return { token: data.token, expires_at: data.expires_at };
        } catch (err) {
            return { token: null, error: err.message };
        }
    });

    // -- Authentication --

    ipcMain.handle('login', async (event, { email, password }) => {
        try {
            // 1. Call standard login endpoint
            const formData = new URLSearchParams();
            formData.append('email', email);
            formData.append('password', password);

            const loginResponse = await fetch(`${CLOUD_API_BASE.replace('/desktop', '')}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString(),
            });

            if (!loginResponse.ok) {
                const errData = await loginResponse.json();
                return { success: false, error: errData.detail || 'Login failed' };
            }

            const loginData = await loginResponse.json();
            const token = loginData.access_token;

            // 2. Register this device using the JWT token
            const deviceId = require('crypto').randomUUID();
            const regResponse = await fetch(`${CLOUD_API_BASE}/auth/register-client`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    device_name: `LexiFlow Desktop - ${require('os').hostname()}`,
                    device_id: deviceId,
                    os_info: `${require('os').platform()} ${require('os').release()}`,
                }),
            });

            if (!regResponse.ok) {
                return { success: false, error: 'Failed to register desktop client' };
            }

            const regData = await regResponse.json();
            
            // 3. Store credentials
            config.set('apiKey', regData.api_key);
            config.set('clientId', regData.client_id);
            config.set('userEmail', email);

            // 4. Switch to main dashboard
            mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
            
            return { success: true };
        } catch (err) {
            return { success: false, error: err.message };
        }
    });

    ipcMain.handle('logout', async () => {
        config.delete('apiKey');
        config.delete('clientId');
        config.delete('userEmail');
        mainWindow.loadFile(path.join(__dirname, 'renderer', 'login.html'));
        return { success: true };
    });

    // -- Settings Management --

    ipcMain.handle('get-setting', (event, key) => {
        return config.get(key);
    });

    ipcMain.handle('set-setting', (event, { key, value }) => {
        config.set(key, value);
        
        // Handle specific setting side effects
        if (key === 'launchOnStartup') {
            app.setLoginItemSettings({
                openAtLogin: value,
                path: app.getPath('exe'),
            });
        }
        
        return { status: 'saved' };
    });

    ipcMain.handle('get-app-version', () => {
        return app.getVersion();
    });
}

// =========================================================================
// App Lifecycle
// =========================================================================

app.whenReady().then(async () => {
    createWindow();
    registerIpcHandlers();

    // Initialize tray
    const trayIconPath = path.join(__dirname, 'app-icon.png');
    createTray(mainWindow, trayIconPath);

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