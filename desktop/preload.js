/**
 * LexiFlow Desktop — Preload Script (IPC Bridge)
 * 
 * Exposes secure API to the renderer process via contextBridge.
 * The renderer never has direct access to Node.js or Electron APIs.
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('lexiflow', {
    // ========== Folder Management ==========
    
    /** Open the native folder picker dialog. */
    pickFolder: () => ipcRenderer.invoke('pick-folder'),
    
    /** Get all registered sync folders from the cloud. */
    getFolders: () => ipcRenderer.invoke('get-folders'),
    
    /** Remove a folder from sync. */
    removeFolder: (folderId) => ipcRenderer.invoke('remove-folder', folderId),

    /** Fired when a folder is successfully registered. */
    onFolderRegistered: (callback) => {
        ipcRenderer.on('folder-registered', (event, data) => callback(data));
    },

    /** Fired when folder registration fails. */
    onFolderError: (callback) => {
        ipcRenderer.on('folder-error', (event, data) => callback(data));
    },

    // ========== Document Sync ==========
    
    /** Start the background sync engine. */
    startSync: () => ipcRenderer.invoke('start-sync'),
    
    /** Stop the background sync engine. */
    stopSync: () => ipcRenderer.invoke('stop-sync'),
    
    /** Get current sync engine status. */
    getSyncStatus: () => ipcRenderer.invoke('get-sync-status'),
    
    /** Force an immediate sync of all folders. */
    syncNow: () => ipcRenderer.invoke('sync-now'),

    // ========== PII/PHI Redaction ==========
    
    /** Scan a file for PII patterns and return findings. */
    scanFileForPII: (filePath) => ipcRenderer.invoke('scan-file-for-pii', filePath),
    
    /** Redact PII from a document (creates a redacted copy). */
    redactDocument: (filePath) => ipcRenderer.invoke('redact-document', filePath),

    // ========== Cloud Connectivity ==========
    
    /** Check if the cloud API is reachable. */
    checkCloudConnection: () => ipcRenderer.invoke('check-cloud-connection'),
});