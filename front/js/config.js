// config.js - Centralized configuration for frontend
(() => {
  // Backend configuration
  const config = {
    // Will be set by init function
    backendURL: 'http://127.0.0.1:8000',
    wsURL: 'ws://127.0.0.1:8000',
    
    // Check if running in Electron
    isElectron: typeof window !== 'undefined' && window.electronAPI !== undefined,
    
    // Initialize configuration (idempotent)
    async init() {
      if (config._initPromise) return config._initPromise;

      config._initPromise = (async () => {
        if (config.isElectron) {
          try {
            // Get backend URL from Electron main process
            const url = await window.electronAPI.getBackendURL();
            config.backendURL = url;
            // Derive ws from http/https
            config.wsURL = url.replace('https://', 'wss://').replace('http://', 'ws://');
            console.log('[Config] Running in Electron, backend URL:', url, 'ws:', config.wsURL);
          } catch (error) {
            console.warn('[Config] Failed to get Electron backend URL, using default');
          }
        } else {
          // Running in regular browser (development)
          console.log('[Config] Running in browser, using default URLs');
        }
        return config;
      })();

      return config._initPromise;
    },
    
    // Get full API endpoint
    getAPIEndpoint(path) {
      return `${this.backendURL}${path}`;
    },

    // Ready helper
    ready() {
      return config._initPromise || config.init();
    }
  };
  
  // Expose config globally
  window.AppConfig = config;
  
  console.log('[Config] Configuration module loaded');
})();
