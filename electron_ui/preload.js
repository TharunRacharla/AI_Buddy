const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  resizeWindow: (bounds) => ipcRenderer.send('resize-window', bounds),
});
