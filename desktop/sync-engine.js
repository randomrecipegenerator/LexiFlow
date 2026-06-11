/**
 * LexiFlow Desktop — Local Sync Engine
 * 
 * Background module that:
 * - Watches registered local folders for new/modified files
 * - Computes file hashes and compares with cloud metadata
 * - Uploads metadata for new files to the cloud API
 * - Reports sync status back to the main process
 * - Respects sync_interval_seconds from cloud config
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const chokidar = require('chokidar');
const fetch = require('node-fetch');

class SyncEngine {
    constructor(options) {
        this.apiBase = options.apiBase;
        this.getApiKey = options.getApiKey;
        this.syncInterval = options.syncInterval || 300; // seconds
        this.watchers = new Map();   // folderId -> chokidar watcher
        this.folders = new Map();    // folderId -> folderInfo
        this.syncTimer = null;
        this.running = false;
        this.status = {
            state: 'idle',
            totalFolders: 0,
            totalFiles: 0,
            syncedFiles: 0,
            pendingFiles: 0,
            lastSyncAt: null,
            errors: [],
        };
    }

    // =========================================================================
    // Lifecycle
    // =========================================================================

    start() {
        if (this.running) return;
        this.running = true;
        this.status.state = 'running';
        console.log('[SyncEngine] Started');

        // Periodic sync
        this.syncTimer = setInterval(() => {
            this.syncAll();
        }, this.syncInterval * 1000);

        // Initial sync
        this.syncAll();
    }

    stop() {
        this.running = false;
        this.status.state = 'stopped';
        if (this.syncTimer) {
            clearInterval(this.syncTimer);
            this.syncTimer = null;
        }
        for (const [folderId, watcher] of this.watchers) {
            watcher.close();
        }
        this.watchers.clear();
        console.log('[SyncEngine] Stopped');
    }

    // =========================================================================
    // Folder Watching
    // =========================================================================

    watchFolder(folderId, localPath) {
        if (this.watchers.has(folderId)) {
            console.log(`[SyncEngine] Already watching ${folderId}`);
            return;
        }

        if (!fs.existsSync(localPath)) {
            console.error(`[SyncEngine] Path does not exist: ${localPath}`);
            this.status.errors.push({ folderId, error: 'Path does not exist' });
            return;
        }

        const watcher = chokidar.watch(localPath, {
            persistent: true,
            ignoreInitial: true,
            depth: 5,
            awaitWriteFinish: { stabilityThreshold: 2000, pollInterval: 100 },
            ignored: /(^|[\/\\])\../, // ignore dotfiles
        });

        watcher.on('add', (filePath) => {
            console.log(`[SyncEngine] New file detected: ${filePath}`);
            this.processFile(filePath, folderId);
        });

        watcher.on('change', (filePath) => {
            console.log(`[SyncEngine] File changed: ${filePath}`);
            this.processFile(filePath, folderId);
        });

        watcher.on('unlink', (filePath) => {
            console.log(`[SyncEngine] File removed: ${filePath}`);
        });

        watcher.on('error', (err) => {
            console.error(`[SyncEngine] Watch error: ${err.message}`);
            this.status.errors.push({ folderId, error: err.message });
        });

        this.watchers.set(folderId, watcher);
        this.folders.set(folderId, { folderId, localPath });
        this.status.totalFolders = this.folders.size;

        console.log(`[SyncEngine] Now watching: ${localPath} (${folderId})`);
    }

    unwatchFolder(folderId) {
        const watcher = this.watchers.get(folderId);
        if (watcher) {
            watcher.close();
            this.watchers.delete(folderId);
            this.folders.delete(folderId);
            this.status.totalFolders = this.folders.size;
            console.log(`[SyncEngine] Stopped watching: ${folderId}`);
        }
    }

    // =========================================================================
    // File Processing
    // =========================================================================

    async processFile(filePath, folderId) {
        const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.docx', '.txt', '.csv'];
        const ext = path.extname(filePath).toLowerCase();
        if (!allowedExtensions.includes(ext)) {
            return; // Skip unsupported file types
        }

        try {
            const stats = fs.statSync(filePath);
            const fileHash = await this.computeHash(filePath);
            const fileName = path.basename(filePath);

            // Build metadata to send to cloud
            const metadata = {
                file_name: fileName,
                file_path: filePath,
                file_size_bytes: stats.size,
                file_hash: fileHash,
                mime_type: this.getMimeType(ext),
                folder_id: folderId,
                tags: [ext.replace('.', '')],
            };

            // Send to cloud API
            const apiKey = await this.getApiKey();
            const response = await fetch(`${this.apiBase}/documents/sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey,
                },
                body: JSON.stringify([metadata]),
            });

            if (response.ok) {
                this.status.syncedFiles++;
                console.log(`[SyncEngine] Synced: ${fileName}`);
            } else {
                this.status.errors.push({
                    folderId,
                    file: fileName,
                    error: `HTTP ${response.status}`,
                });
            }
        } catch (err) {
            console.error(`[SyncEngine] Error processing ${filePath}: ${err.message}`);
            this.status.errors.push({ folderId, file: filePath, error: err.message });
        }

        this.status.totalFiles = this.status.syncedFiles + this.status.pendingFiles;
    }

    async syncAll() {
        console.log('[SyncEngine] Sync cycle started');
        this.status.state = 'syncing';

        for (const [folderId, folder] of this.folders) {
            try {
                const files = await this.scanFolder(folder.localPath);
                const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.docx', '.txt', '.csv'];
                const documents = [];

                for (const filePath of files) {
                    const ext = path.extname(filePath).toLowerCase();
                    if (!allowedExtensions.includes(ext)) continue;

                    const stats = fs.statSync(filePath);
                    const fileHash = await this.computeHash(filePath);
                    documents.push({
                        file_name: path.basename(filePath),
                        file_path: filePath,
                        file_size_bytes: stats.size,
                        file_hash: fileHash,
                        mime_type: this.getMimeType(ext),
                        folder_id: folderId,
                        tags: [ext.replace('.', '')],
                    });
                }

                if (documents.length > 0) {
                    const apiKey = await this.getApiKey();
                    const response = await fetch(`${this.apiBase}/documents/sync`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-API-Key': apiKey,
                        },
                        body: JSON.stringify(documents),
                    });

                    if (response.ok) {
                        const result = await response.json();
                        this.status.syncedFiles += result.count || documents.length;
                        this.status.pendingFiles = 0;
                    }
                }

                // Update cloud sync status
                const apiKey = await this.getApiKey();
                await fetch(`${this.apiBase}/folders/${folderId}/sync-status`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey,
                    },
                    body: JSON.stringify({
                        folder_id: folderId,
                        status: 'idle',
                        total_files: this.status.totalFiles,
                        synced_files: this.status.syncedFiles,
                        pending_files: 0,
                    }),
                });
            } catch (err) {
                console.error(`[SyncEngine] Sync error for folder ${folderId}: ${err.message}`);
                this.status.errors.push({ folderId, error: err.message });
            }
        }

        this.status.lastSyncAt = new Date().toISOString();
        this.status.state = 'idle';
        console.log(`[SyncEngine] Sync cycle complete. ${this.status.syncedFiles} files synced.`);
    }

    // =========================================================================
    // Helpers
    // =========================================================================

    scanFolder(dirPath) {
        const files = [];
        try {
            const entries = fs.readdirSync(dirPath, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                if (entry.isDirectory()) {
                    if (!entry.name.startsWith('.')) {
                        files.push(...this.scanFolder(fullPath));
                    }
                } else if (entry.isFile()) {
                    files.push(fullPath);
                }
            }
        } catch (err) {
            console.error(`[SyncEngine] Scan error: ${err.message}`);
        }
        return files;
    }

    computeHash(filePath) {
        return new Promise((resolve, reject) => {
            const hash = crypto.createHash('sha256');
            const stream = fs.createReadStream(filePath);
            stream.on('data', (data) => hash.update(data));
            stream.on('end', () => resolve(hash.digest('hex')));
            stream.on('error', (err) => reject(err));
        });
    }

    getMimeType(ext) {
        const mimeMap = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        };
        return mimeMap[ext] || 'application/octet-stream';
    }

    getStatus() {
        return {
            ...this.status,
            watchedFolders: Array.from(this.folders.keys()),
        };
    }
}

module.exports = { SyncEngine };