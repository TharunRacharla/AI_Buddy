const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

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
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js'),
    allowRunningInsecureContent: true,   
    webSecurity: false,   
    }
  });

  mainWindow.webContents.session.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === 'media') callback(true);  // allow mic
    else callback(false);
  });
  mainWindow.loadFile('index.html');
  mainWindow.setVisibleOnAllWorkspaces(true);
}

// Handle window resize from renderer
ipcMain.on('resize-window', (event, { width, height }) => {
  const { height: screenH } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow.setBounds({
    width: width,
    height: height,
    x: 20,                        // always stay on left side
    y: screenH - height - 20      // grow upward from bottom
  }, true);
});

ipcMain.on('drag-window', (event, { mouseX, mouseY }) => {
  const [winX, winY] = mainWindow.getPosition();
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());