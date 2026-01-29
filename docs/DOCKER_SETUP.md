# Docker Setup Guide

This guide explains how to run FreqAiPro using Docker and Docker Compose, as well as how to modify and customize the Docker configuration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Running Docker Containers](#running-docker-containers)
5. [Stopping Containers](#stopping-containers)
6. [Viewing Logs](#viewing-logs)
7. [Editing Docker Configuration](#editing-docker-configuration)
8. [Customizing Dockerfiles](#customizing-dockerfiles)
9. [Environment Variables](#environment-variables)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 1.29 or higher

### Installing Docker and Docker Compose

#### On Linux (Ubuntu/Debian):
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### On macOS:
```bash
# Using Homebrew
brew install docker docker-compose
```

#### On Windows:
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

## Quick Start

### Start All Services (Backend + Frontend)

```bash
cd /root/FreqAiPro
docker-compose up -d
```

This command:
- Builds Docker images (if not already built)
- Starts backend container on port 5000
- Starts frontend container on port 3000
- Runs in detached mode (`-d` flag)

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

### Stop All Services

```bash
docker-compose down
```

## Project Structure

```
/root/FreqAiPro/
├── Dockerfile.backend          # Backend container configuration
├── Dockerfile.frontend         # Frontend container configuration
├── docker-compose.yml          # Orchestration configuration
├── app.py                      # Flask backend application
├── requirements.txt            # Python dependencies
├── frontend/
│   ├── package.json            # Node.js dependencies
│   ├── next.config.js          # Next.js configuration
│   └── src/                    # React source code
├── docs/
│   └── DOCKER_SETUP.md        # This file
└── logs/
    ├── app.log                 # Flask logs
    └── flask.log               # Development server logs
```

## Running Docker Containers

### Build Images Manually

```bash
# Build both images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend

# Build without cache (fresh build)
docker-compose build --no-cache
```

### Start Services

```bash
# Start in background (detached mode)
docker-compose up -d

# Start and view logs in real-time
docker-compose up

# Start specific services only
docker-compose up -d backend
docker-compose up -d frontend
```

### Rebuild and Start (useful after code changes)

```bash
docker-compose up -d --build
```

### Scale Services

```bash
# Run multiple instances of a service
docker-compose up -d --scale backend=2
```

## Stopping Containers

### Stop All Services

```bash
# Stop without removing containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (removes data)
docker-compose down -v
```

### Stop Specific Services

```bash
docker-compose stop backend
docker-compose stop frontend
```

## Viewing Logs

### View Container Logs

```bash
# View all services logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time (-f flag)
docker-compose logs -f backend

# View last 50 lines
docker-compose logs --tail=50 backend

# View logs with timestamps
docker-compose logs --timestamps backend
```

### Inside Container Logs

```bash
# Access Flask logs from container
docker-compose exec backend cat logs/app.log

# Stream Flask logs
docker-compose exec backend tail -f logs/app.log

# View frontend logs
docker-compose exec frontend npm logs
```

## Editing Docker Configuration

### Editing docker-compose.yml

The `docker-compose.yml` file orchestrates both services. Key sections:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: freqaipro-backend
    ports:
      - "5000:5000"  # Host:Container port mapping
    volumes:
      - ./:/app      # Mount current directory
    environment:
      - FLASK_ENV=production
      - FLASK_APP=app.py

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: freqaipro-frontend
    ports:
      - "3000:3000"  # Host:Container port mapping
    depends_on:
      - backend      # Frontend waits for backend
```

### Changing Ports

Edit `docker-compose.yml` and modify the `ports` section:

```yaml
# Change frontend port from 3000 to 8000
frontend:
  ports:
    - "8000:3000"  # Access at localhost:8000

# Change backend port from 5000 to 8080
backend:
  ports:
    - "8080:5000"  # Access at localhost:8080
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Adding Environment Variables

Edit `docker-compose.yml` and add to the `environment` section:

```yaml
backend:
  environment:
    - FLASK_ENV=production
    - DEBUG=false
    - REDIS_URL=redis://redis:6379
    - DATABASE_URL=sqlite:///signals.db
```

Or create a `.env` file in the root directory:

```bash
# .env
FLASK_ENV=production
DEBUG=false
REDIS_URL=redis://redis:6379
```

Then reference in `docker-compose.yml`:

```yaml
backend:
  env_file: .env
```

## Customizing Dockerfiles

### Backend Dockerfile (Dockerfile.backend)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py app.py
COPY strategy.py strategy.py
COPY *.db ./

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
```

**Common Customizations:**

1. **Add Python Packages**: Modify `requirements.txt`
2. **Change Python Version**: Replace `FROM python:3.10-slim` with desired version
3. **Install System Libraries**: Add to `apt-get install` command
4. **Change Working Directory**: Modify `WORKDIR`

### Frontend Dockerfile (Dockerfile.frontend)

```dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend/src ./src
COPY frontend/public ./public 2>/dev/null || true
COPY frontend/next.config.js frontend/tsconfig.json frontend/tailwind.config.ts ./

# Build Next.js application
RUN npm run build

# Expose port
EXPOSE 3000

# Run Next.js
CMD ["npm", "start"]
```

**Common Customizations:**

1. **Change Node Version**: Replace `FROM node:20-alpine` with desired version
2. **Add Build Arguments**: Use `ARG` directive for build-time variables
3. **Change Port**: Modify `EXPOSE` and startup command

### Example: Custom Backend with Additional Services

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including Redis CLI
RUN apt-get update && apt-get install -y \
    gcc \
    redis-tools \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/')"

EXPOSE 5000

CMD ["python", "app.py"]
```

## Environment Variables

### Backend Environment Variables

Set in `docker-compose.yml` or `.env`:

```yaml
environment:
  - FLASK_ENV=production          # production or development
  - FLASK_DEBUG=0                 # 1 for debug mode
  - REDIS_URL=redis://redis:6379  # Redis connection
  - DATABASE_URL=sqlite:///app.db  # Database connection
  - LOG_LEVEL=INFO                # Logging level
  - SECRET_KEY=your-secret-key    # Flask secret key
```

### Frontend Environment Variables

Create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=FreqAiPro
```

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Check if ports are already in use
sudo lsof -i :5000
sudo lsof -i :3000

# Kill process on specific port (Linux/macOS)
sudo kill -9 $(lsof -t -i:5000)
```

### Port Already in Use

Change ports in `docker-compose.yml`:

```yaml
backend:
  ports:
    - "5001:5000"  # Use 5001 instead of 5000

frontend:
  ports:
    - "3001:3000"  # Use 3001 instead of 3000
```

### API Connection Issues

Ensure backend container is running:

```bash
docker-compose ps
```

Check if frontend can reach backend:

```bash
docker-compose exec frontend curl http://backend:5000
```

Update `frontend/.env.local` if needed:

```
NEXT_PUBLIC_API_URL=http://backend:5000  # Use service name in container
```

### Out of Disk Space

Clean up unused Docker resources:

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Complete cleanup
docker system prune -a
```

### Rebuild from Scratch

```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Rebuild everything
docker-compose up -d --build
```

### Check Container Resource Usage

```bash
# View container stats
docker stats

# View specific container
docker stats freqaipro-backend freqaipro-frontend
```

## Advanced Docker Operations

### Execute Commands Inside Containers

```bash
# Run Python command in backend
docker-compose exec backend python -c "import sys; print(sys.version)"

# Run npm command in frontend
docker-compose exec frontend npm list

# Access shell in container
docker-compose exec backend sh
docker-compose exec frontend sh
```

### Copy Files Between Host and Container

```bash
# Copy from container to host
docker cp freqaipro-backend:/app/logs/app.log ./logs/

# Copy from host to container
docker cp ./config.json freqaipro-backend:/app/
```

### Network Communication Between Containers

```bash
# Backend is accessible to frontend as 'backend'
# Frontend is accessible to backend as 'frontend'

# From frontend, curl backend:
docker-compose exec frontend curl http://backend:5000

# From backend, check frontend:
docker-compose exec backend curl http://frontend:3000
```

## Production Deployment Tips

### Use .env File for Secrets

```bash
# .env (add to .gitignore)
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@db:5432/freqaipro
REDIS_URL=redis://redis:6379
```

### Use Specific Image Tags

```yaml
# Instead of 'latest'
backend:
  image: freqaipro-backend:1.0.0

# Or use git commit SHA
backend:
  image: freqaipro-backend:${GIT_COMMIT}
```

### Add Resource Limits

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

### Health Checks

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5000/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 10s
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Next.js with Docker](https://nextjs.org/docs/deployment/docker)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)
