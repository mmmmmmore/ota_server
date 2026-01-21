# OTA Management - Docker Deployment (Optional)

This guide explains how to containerize and deploy the OTA Management backend in Docker for server-based deployments.

## Overview

While the primary use case is the Electron desktop application, the Node.js backend can be deployed in Docker for:
- Centralized OTA management across multiple locations
- Integration with existing infrastructure
- Scalable deployment on servers
- CI/CD pipelines

## Docker Setup

### Prerequisites
- Docker installed (https://www.docker.com/products/docker-desktop)
- Docker Compose (usually included with Docker Desktop)

### Create Dockerfile

Create `backend_nodejs/Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --production

# Copy application
COPY . .

# Create data directories
RUN mkdir -p /app/data/db /app/data/firmware /app/data/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8000/api/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start server
CMD ["node", "server.js"]
```

### Create Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  ota-backend:
    build:
      context: .
      dockerfile: backend_nodejs/Dockerfile
    container_name: ota-management-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./backend_nodejs:/app
    environment:
      - NODE_ENV=production
      - PORT=8000
      - HOST=0.0.0.0
      - DB_PATH=/app/data/db
      - FIRMWARE_PATH=/app/data/firmware
      - GW_IP=192.168.4.1
      - GW_TCP_PORT=9001
    restart: unless-stopped
    networks:
      - ota-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  ota-network:
    driver: bridge

volumes:
  data:
    driver: local
```

### Create .dockerignore

Create `backend_nodejs/.dockerignore`:

```
node_modules
npm-debug.log
dist
.git
.gitignore
*.md
*.yml
.DS_Store
```

## Building & Running

### Build Docker Image

```bash
# Build image
docker build -t ota-management:1.0.0 -f backend_nodejs/Dockerfile .

# Verify build
docker images | grep ota-management
```

### Run Container Directly

```bash
# Create data directory
mkdir -p ./data/db ./data/firmware

# Run container
docker run -d \
  --name ota-backend \
  -p 8000:8000 \
  -v ./data:/app/data \
  -e DB_PATH=/app/data/db \
  -e FIRMWARE_PATH=/app/data/firmware \
  -e GW_IP=192.168.4.1 \
  -e GW_TCP_PORT=9001 \
  ota-management:1.0.0

# View logs
docker logs -f ota-backend

# Stop container
docker stop ota-backend

# Remove container
docker rm ota-backend
```

### Run with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f ota-backend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Configuration

### Environment Variables in Docker

Set via `docker run -e`:

```bash
docker run -e NODE_ENV=production \
           -e PORT=8000 \
           -e HOST=0.0.0.0 \
           -e DB_PATH=/app/data/db \
           -e FIRMWARE_PATH=/app/data/firmware \
           -e GW_IP=192.168.4.1 \
           -e GW_TCP_PORT=9001 \
           ota-management:1.0.0
```

Or in `docker-compose.yml`:

```yaml
environment:
  - NODE_ENV=production
  - DB_PATH=/app/data/db
  - GW_IP=192.168.4.1
```

### Volume Mounting

```bash
# Mount data directory
-v /path/to/host/data:/app/data

# Mount backend source (for development)
-v ./backend_nodejs:/app
```

## Networking

### Container to Device Network

For containers to reach ESP32 devices on custom network:

```yaml
networks:
  - host  # Use host network (caution: less isolation)

# OR

networks:
  custom:
    driver: bridge
    ipam:
      config:
        - subnet: 192.168.0.0/24
```

### Port Mapping

```bash
# Map different port
docker run -p 9000:8000 ota-management:1.0.0
# Access at http://localhost:9000
```

## Data Persistence

### Using Named Volumes

```yaml
volumes:
  ota-data:
    driver: local

services:
  ota-backend:
    volumes:
      - ota-data:/app/data
```

### Using Bind Mounts

```yaml
services:
  ota-backend:
    volumes:
      - /path/to/host/data:/app/data
```

### Backup Data

```bash
# Create backup
docker run --rm \
  -v ota-data:/app/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/ota-data-$(date +%Y%m%d).tar.gz -C /app/data .

# Restore backup
docker run --rm \
  -v ota-data:/app/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/ota-data-20251229.tar.gz -C /app/data
```

## Monitoring & Logging

### View Logs

```bash
# Tail logs
docker logs -f ota-backend

# Last 50 lines with timestamps
docker logs --tail 50 -t ota-backend

# Since specific time
docker logs --since 2024-12-29T10:00:00 ota-backend
```

### Health Checks

```bash
# Manual health check
curl http://localhost:8000/api/health

# From docker-compose
docker-compose exec ota-backend curl http://localhost:8000/api/health

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Performance Monitoring

```bash
# CPU and Memory usage
docker stats ota-backend

# Container inspection
docker inspect ota-backend | jq '.[0].State'
```

## Deployment Scenarios

### Scenario 1: Single Server

```bash
# Start backend service
docker-compose up -d

# Access via http://server-ip:8000
```

### Scenario 2: Raspberry Pi

```bash
# Build for ARM (Raspberry Pi 4)
docker build --platform linux/arm/v7 -t ota-management:rpi .

# Run on Pi
docker run -d \
  -p 8000:8000 \
  -v /home/pi/ota-data:/app/data \
  ota-management:rpi
```

### Scenario 3: Kubernetes (Advanced)

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ota-management
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ota-management
  template:
    metadata:
      labels:
        app: ota-management
    spec:
      containers:
      - name: backend
        image: ota-management:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DB_PATH
          value: "/data/db"
        volumeMounts:
        - name: data
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ota-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ota-management
spec:
  selector:
    app: ota-management
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy with:
```bash
kubectl apply -f k8s/deployment.yaml
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs ota-backend

# Inspect container
docker inspect ota-backend

# Common issues:
# - Port 8000 already in use: docker run -p 9000:8000
# - Database corruption: docker exec -it ota-backend rm /app/data/db/devices.json
```

### Permission Denied

```bash
# Fix data directory permissions
chmod 755 ./data
chmod 755 ./data/db
chmod 755 ./data/firmware

# Or run with specific user
docker run --user 1000:1000 -v ./data:/app/data ota-management:1.0.0
```

### Connection to ESP32 Fails

```bash
# Check container network
docker inspect ota-backend | jq '.[0].NetworkSettings.Networks'

# Use host network (if available)
docker run --network host ota-management:1.0.0

# Or specify gateway IP
docker run -e GW_IP=192.168.4.1 ota-management:1.0.0
```

### Out of Memory

```bash
# Limit memory usage
docker run -m 512m --memory-swap 1g ota-management:1.0.0

# Check current usage
docker stats ota-backend --no-stream
```

## Production Checklist

- [ ] Use specific image tags (not `latest`)
- [ ] Set `NODE_ENV=production`
- [ ] Configure volume mounts for data persistence
- [ ] Set resource limits (memory, CPU)
- [ ] Configure logging driver
- [ ] Set up health checks
- [ ] Use restart policies (`unless-stopped`)
- [ ] Configure monitoring and alerts
- [ ] Plan backup strategy
- [ ] Document all environment variables
- [ ] Test disaster recovery

## Cleanup

```bash
# Stop and remove container
docker-compose down

# Remove image
docker rmi ota-management:1.0.0

# Clean up unused containers/images
docker system prune

# Force remove all
docker system prune -a --volumes
```

## Next Steps

1. Build image: `docker build -t ota-management .`
2. Test locally: `docker-compose up`
3. Configure for your network (GW_IP, ports)
4. Deploy to production server
5. Set up monitoring and backups

For additional deployment architectures, contact support.

