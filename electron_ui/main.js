const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  const { height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: 85,
    height: 80,
    x: 20,
    y: height - 100,
    frame: false,
    transparent: true,
    alwaysOnTop: false,
    resizable: false,
    skipTaskbar: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.setVisibleOnAllWorkspaces(true);
}

// Handle window resize from renderer
ipcMain.on('resize-window', (event, bounds) => {
  const { width, height } = bounds || {};
  if (
    !mainWindow ||
    mainWindow.isDestroyed() ||
    event.sender !== mainWindow.webContents ||
    !((width === 85 && height === 80) || (width === 415 && height === 470))
  ) {
    console.warn('Rejected invalid resize-window request');
    return;
  }

  const { height: screenH } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow.setBounds({
    width: width,
    height: height,
    x: 20,                        // always stay on left side
    y: screenH - height - 20      // grow upward from bottom
  }, true);
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());