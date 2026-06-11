const { app, BrowserWindow, Menu, globalShortcut } = require('electron');
const path = require('path');
const { createTray, updateTrayMenu } = require('./tray');

// Keep a global reference of the window object
let mainWindow = null;
let tray = null;
const isDev = process.env.NODE_ENV === 'development';

// Path to the LexiFlow dashboard HTML
const DASHBOARD_PATH = path.join(__dirname, '..', 'dashboard.html');

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'LexiFlow Legal Suite',
    icon: path.join(__dirname, 'app-icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
    show: false,
  });

  // Load the dashboard
  mainWindow.loadFile(DASHBOARD_PATH);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Set up the application menu
  const menuTemplate = [
    {
      label: 'LexiFlow',
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        {
          label: 'Preferences',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            mainWindow.webContents.send('navigate', 'settings');
          },
        },
        { type: 'separator' },
        { role: 'quit', label: 'Quit LexiFlow' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        { type: 'separator' },
        { role: 'front' },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  // Create tray icon
  tray = createTray(mainWindow, path.join(__dirname, 'app-icon.png'));
}

// Launch on startup (optional, configurable)
function setLaunchOnStartup(enabled) {
  app.setLoginItemSettings({
    openAtLogin: enabled,
    path: app.getPath('exe'),
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // macOS: re-create window when dock icon is clicked
    if (mainWindow === null) {
      createWindow();
    } else {
      mainWindow.show();
    }
  });

  // Register global shortcuts
  globalShortcut.register('CmdOrCtrl+Shift+L', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
});

app.on('window-all-closed', () => {
  // On macOS, keep app in dock/tray
  if (process.platform !== 'darwin') {
    // Don't quit - let the tray keep running
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
  globalShortcut.unregisterAll();
});

// Expose launch-on-startup to renderer via IPC
const { ipcMain } = require('electron');
ipcMain.handle('get-launch-on-startup', () => {
  return app.getLoginItemSettings().openAtLogin;
});

ipcMain.handle('set-launch-on-startup', (event, enabled) => {
  setLaunchOnStartup(enabled);
  return true;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('minimize-to-tray', () => {
  if (mainWindow) {
    mainWindow.hide();
  }
  return true;
});