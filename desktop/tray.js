const { Tray, Menu, nativeImage, app } = require('electron');

let tray = null;

/**
 * Create and return a system tray icon for the LexiFlow desktop app.
 * @param {BrowserWindow} mainWindow - The main application window
 * @param {string} iconPath - Path to the tray icon PNG
 * @returns {Tray}
 */
function createTray(mainWindow, iconPath) {
  // Create a 22x22 tray icon (or fallback to 16x16)
  const icon = nativeImage.createFromPath(iconPath);
  const trayIcon = icon.isEmpty()
    ? nativeImage.createEmpty()
    : icon.resize({ width: 22, height: 22 });

  tray = new Tray(trayIcon);
  tray.setToolTip('LexiFlow Legal Suite');

  updateTrayMenu(mainWindow);

  // Double-click to show window
  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  return tray;
}

/**
 * Update the tray context menu with current state.
 * @param {BrowserWindow} mainWindow
 */
function updateTrayMenu(mainWindow) {
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show LexiFlow',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    {
      label: 'Dashboard',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.loadFile(path.join(__dirname, 'renderer', 'desktop-settings.html'));
        }
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
}

module.exports = { createTray, updateTrayMenu };