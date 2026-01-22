# Certificate Management

This directory contains SSL/TLS certificates for the OTA Management Server.

## Directory Structure

```
certs/
├── ca/                     # Certificate Authority files
│   ├── rootCA.pem         # Root CA certificate (public)
│   └── rootCA.key         # Root CA private key (keep secure!)
│
└── server/                 # Server certificates
    ├── server.key         # Server private key
    ├── server.crt         # Server certificate
    ├── server_key.pem     # Server private key (PEM format)
    ├── server_cert.pem    # Server certificate (PEM format)
    ├── fullchain.pem      # Full certificate chain
    └── san.cnf            # Subject Alternative Name config
```

## File Descriptions

### CA Files
- **rootCA.pem**: Root Certificate Authority certificate used to sign server certificates
- **rootCA.key**: Root CA private key (required for signing new certificates)

### Server Files
- **server.key / server_key.pem**: Server private key (never share this!)
- **server.crt / server_cert.pem**: Server certificate signed by the CA
- **fullchain.pem**: Complete certificate chain (server cert + CA cert)
- **san.cnf**: OpenSSL configuration for Subject Alternative Names (SANs)

## Usage in Node.js

```javascript
const fs = require('fs');
const path = require('path');

const certOptions = {
  key: fs.readFileSync(path.join(__dirname, 'certs/server/server.key')),
  cert: fs.readFileSync(path.join(__dirname, 'certs/server/server.crt')),
  ca: fs.readFileSync(path.join(__dirname, 'certs/ca/rootCA.pem'))
};
```

## Security Notes

⚠️ **IMPORTANT**:
- Never commit private keys (.key files) to version control
- Keep `rootCA.key` secure - it can sign certificates for your domain
- Use `.gitignore` to exclude sensitive files
- Rotate certificates before expiration
- Use strong passphrases for production keys

## Generate New Certificates

To generate new server certificates:

```bash
# Generate server private key
openssl genrsa -out certs/server/server.key 2048

# Create certificate signing request
openssl req -new -key certs/server/server.key \
  -out certs/server/server.csr \
  -config certs/server/san.cnf

# Sign with CA
openssl x509 -req -in certs/server/server.csr \
  -CA certs/ca/rootCA.pem \
  -CAkey certs/ca/rootCA.key \
  -CAcreateserial \
  -out certs/server/server.crt \
  -days 365 \
  -extensions v3_req \
  -extfile certs/server/san.cnf
```

## Certificate Expiration

Check certificate expiration dates:

```bash
# Check server certificate
openssl x509 -in certs/server/server.crt -noout -dates

# Check CA certificate
openssl x509 -in certs/ca/rootCA.pem -noout -dates
```
