# LexiFlow Desktop App

**Electron wrapper for the LexiFlow Attorney Dashboard.**

## Quick Start

```bash
cd desktop
npm install
npm start
```

## Development

```bash
npm run dev    # Starts with DevTools open
```

## Build for Distribution

```bash
npm run build:win    # Windows .exe (NSIS installer)
npm run build:mac    # macOS .dmg
npm run build:all    # All platforms
```

Output goes to `desktop/dist/`.

## Features

- **System Tray**: Minimize to tray with context menu (Show, Dashboard, Settings, Quit)
- **Launch on Startup**: Configurable via Settings (IPC)
- **Global Shortcut**: `Cmd/Ctrl+Shift+L` to bring window to front
- **Native Menus**: Standard app menu with LexiFlow branding

## Project Structure

```
desktop/
├── main.js              # Electron main process
├── preload.js            # Secure context bridge (IPC)
├── tray.js               # System tray management
├── app-icon.png          # App icon (256x256)
├── generate-icon.js      # Icon generator script
├── package.json          # Dependencies & build config
└── .gitignore
```

## Tech Stack

- Electron 33.x
- electron-builder 25.x
- Context isolation enabled
- Sandbox enabled