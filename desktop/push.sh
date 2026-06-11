#!/bin/bash
cd /home/team/shared/LexiFlow-Final
echo "=== Current branch ==="
git branch --show-current
echo "=== Trying to switch to feat/desktop-app ==="
git checkout feat/desktop-app 2>&1 || git checkout -b feat/desktop-app 2>&1
echo "=== After checkout ==="
git branch --show-current
echo "=== Adding desktop files ==="
git add desktop/package.json desktop/main.js desktop/preload.js desktop/tray.js desktop/app-icon.png desktop/generate-icon.js desktop/README.md desktop/.gitignore
echo "=== Status ==="
git status --short -- desktop/
echo "=== Committing ==="
git commit -m "feat: initialize LexiFlow Desktop Electron wrapper" --allow-empty -m "- Electron 33.x main process with tray icon and window management
- Secure preload bridge with contextIsolation enabled
- System tray with context menu (Show, Dashboard, Settings, Quit)
- Global shortcut Cmd/Ctrl+Shift+L to bring window to front
- Launch-on-startup support via IPC
- Build pipeline for Windows (.exe NSIS), macOS (.dmg), Linux (.AppImage)
- Loads dashboard.html as the main application window
- 256x256 app icon with LF brand mark"
echo "=== Pushing ==="
git push -u origin feat/desktop-app 2>&1