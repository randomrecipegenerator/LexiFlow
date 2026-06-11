const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('lexiflowDesktop', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),

  // Window management
  minimizeToTray: () => ipcRenderer.invoke('minimize-to-tray'),

  // Launch on startup
  getLaunchOnStartup: () => ipcRenderer.invoke('get-launch-on-startup'),
  setLaunchOnStartup: (enabled) => ipcRenderer.invoke('set-launch-on-startup', enabled),

  // Navigation listener (from menu)
  onNavigate: (callback) => {
    ipcRenderer.on('navigate', (event, route) => callback(route));
  },

  // Notifications
  showNotification: (title, body) => {
    new Notification(title, { body });
  },
});