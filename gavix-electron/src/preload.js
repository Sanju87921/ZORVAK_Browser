const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('gavix', {
  searchBackendUrl: process.env.GAVIX_SEARCH_URL || 'http://127.0.0.1:8000'
});
