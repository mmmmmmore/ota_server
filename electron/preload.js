/**
 * Preload script for Electron
 * This script runs in a special context that has access to both Node.js APIs
 * and the DOM, acting as a secure bridge between main and renderer processes.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Get backend URL configuration
  getBackendURL: () => ipcRenderer.invoke('get-backend-url'),
  
  // File selection dialog
  selectFile: () => ipcRenderer.invoke('select-file'),
  
  // Platform information
  platform: process.platform,
  
  // App version
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  }
});

// Expose console methods for better debugging
contextBridge.exposeInMainWorld('electronConsole', {
  log: (...args) => console.log('[Renderer]:', ...args),
  error: (...args) => console.error('[Renderer Error]:', ...args),
  warn: (...args) => console.warn('[Renderer Warning]:', ...args),
  info: (...args) => console.info('[Renderer Info]:', ...args)
});

console.log('Preload script loaded successfully');
