/**
 * Certificate Manager - SSL/TLS Certificate Management
 * Handles loading and validation of certificates for HTTPS server
 */

const fs = require('fs');
const path = require('path');

class CertManager {
  constructor(certsDir) {
    this.certsDir = certsDir || path.join(__dirname, '..', '..', 'certs');
    this.caDir = path.join(this.certsDir, 'ca');
    this.serverDir = path.join(this.certsDir, 'server');
  }

  /**
   * Check if all required certificate files exist
   */
  validate() {
    const required = [
      path.join(this.serverDir, 'server.key'),
      path.join(this.serverDir, 'server.crt'),
      path.join(this.caDir, 'rootCA.pem')
    ];

    const missing = required.filter(file => !fs.existsSync(file));
    
    if (missing.length > 0) {
      console.error('[CertManager] Missing certificate files:');
      missing.forEach(file => console.error(`  - ${file}`));
      return false;
    }

    return true;
  }

  /**
   * Load SSL options for HTTPS server
   * @returns {Object|null} SSL options or null if certificates not available
   */
  loadSSLOptions() {
    if (!this.validate()) {
      console.warn('[CertManager] Certificate validation failed');
      return null;
    }

    try {
      const options = {
        // Server private key
        key: fs.readFileSync(path.join(this.serverDir, 'server.key')),
        
        // Server certificate
        cert: fs.readFileSync(path.join(this.serverDir, 'server.crt')),
        
        // Certificate Authority
        ca: fs.readFileSync(path.join(this.caDir, 'rootCA.pem')),
        
        // Optional: Use fullchain if available
        // cert: fs.readFileSync(path.join(this.serverDir, 'fullchain.pem')),
        
        // SSL/TLS options
        requestCert: false,
        rejectUnauthorized: false,
        minVersion: 'TLSv1.2'
      };

      console.log('[CertManager] SSL certificates loaded successfully');
      console.log(`[CertManager] Server key: ${path.join(this.serverDir, 'server.key')}`);
      console.log(`[CertManager] Server cert: ${path.join(this.serverDir, 'server.crt')}`);
      console.log(`[CertManager] CA cert: ${path.join(this.caDir, 'rootCA.pem')}`);

      return options;
    } catch (err) {
      console.error('[CertManager] Failed to load certificates:', err.message);
      return null;
    }
  }

  /**
   * Get certificate expiration dates
   */
  getCertInfo() {
    const certPath = path.join(this.serverDir, 'server.crt');
    
    if (!fs.existsSync(certPath)) {
      return null;
    }

    try {
      const { execSync } = require('child_process');
      const output = execSync(`openssl x509 -in ${certPath} -noout -dates`, { encoding: 'utf-8' });
      
      const lines = output.split('\n');
      const notBefore = lines[0].replace('notBefore=', '').trim();
      const notAfter = lines[1].replace('notAfter=', '').trim();

      return {
        notBefore,
        notAfter,
        isValid: new Date(notAfter) > new Date()
      };
    } catch (err) {
      console.error('[CertManager] Failed to get certificate info:', err.message);
      return null;
    }
  }

  /**
   * Alternative loading method using PEM format files
   */
  loadPEMOptions() {
    try {
      const options = {
        key: fs.readFileSync(path.join(this.serverDir, 'server_key.pem')),
        cert: fs.readFileSync(path.join(this.serverDir, 'server_cert.pem')),
        ca: fs.readFileSync(path.join(this.caDir, 'rootCA.pem'))
      };
      
      console.log('[CertManager] PEM format certificates loaded successfully');
      return options;
    } catch (err) {
      console.error('[CertManager] Failed to load PEM certificates:', err.message);
      return null;
    }
  }

  /**
   * Load certificate with fullchain
   */
  loadFullchainOptions() {
    const fullchainPath = path.join(this.serverDir, 'fullchain.pem');
    
    if (!fs.existsSync(fullchainPath)) {
      console.warn('[CertManager] fullchain.pem not found, using regular cert');
      return this.loadSSLOptions();
    }

    try {
      const options = {
        key: fs.readFileSync(path.join(this.serverDir, 'server.key')),
        cert: fs.readFileSync(fullchainPath),
        minVersion: 'TLSv1.2'
      };
      
      console.log('[CertManager] Fullchain certificate loaded successfully');
      return options;
    } catch (err) {
      console.error('[CertManager] Failed to load fullchain certificate:', err.message);
      return null;
    }
  }
}

module.exports = CertManager;
