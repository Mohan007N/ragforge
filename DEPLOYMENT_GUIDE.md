# 🚀 RAGForge Production Deployment Guide

A comprehensive, step-by-step guide to deploying RAGForge in production across self-hosted VPS, Docker Compose, PaaS providers (Render, Railway), decoupled serverless setups (Vercel + Cloud Backend), and major cloud platforms (AWS, GCP).

---

## 📑 Table of Contents
1. [Architecture & Storage Overview](#1-architecture--storage-overview)
2. [Strategy 1: Self-Hosted Docker Compose (Recommended for VPS)](#2-strategy-1-self-hosted-docker-compose-vps)
3. [Strategy 2: Render.com (Easiest Cloud PaaS)](#3-strategy-2-rendercom-paas)
4. [Strategy 3: Railway.app](#4-strategy-3-railwayapp)
5. [Strategy 4: Decoupled Setup (Vercel + Cloud Backend)](#5-strategy-4-decoupled-setup-vercel--cloud-backend)
6. [Strategy 5: AWS EC2 / ECS](#6-strategy-5-aws-ec2--ecs)
7. [Strategy 6: Google Cloud Run](#7-strategy-6-google-cloud-run)
8. [SSL / HTTPS Configuration](#8-ssl--https-configuration)
9. [Backup & Disaster Recovery](#9-backup--disaster-recovery)
10. [Production Security Checklist](#10-production-security-checklist)

---

## 1. Architecture & Storage Overview

RAGForge consists of two main tiers:
1. **Frontend**: React 18 + Vite SPA styled with modern CSS and glassmorphism.
2. **Backend**: FastAPI with Gunicorn/Uvicorn workers, LangChain, SentenceTransformers, ChromaDB vector store, and BM25 search.

### ⚠️ Critical Storage Persistence Note
RAGForge stores state in the following filesystem directories:
- `/app/data/documents` — Raw uploaded PDFs.
- `/app/storage/chroma` — ChromaDB vector database embeddings.
- `/app/storage/bm25` — BM25 keyword inverted indices.

> [!IMPORTANT]
> **Always mount persistent volumes to `/app/storage` and `/app/data`**. If running on ephemeral cloud instances without persistent disks, uploaded documents and indexed vectors will be reset on restarts.

---

## 2. Strategy 1: Self-Hosted Docker Compose (VPS)

Ideal for DigitalOcean Droplets, Hetzner, Linode, or AWS EC2 instances ($5–$20/mo).

### Prerequisites
- Ubuntu 22.04 LTS or Debian 12
- Docker Engine 24+ & Docker Compose v2+ installed
- A domain name pointing to your server's public IP (e.g., `rag.yourdomain.com`)

### Step 1: Clone Repository & Configure Environment
```bash
# Clone the repository
git clone https://github.com/Mohan007N/ragforge.git /opt/ragforge
cd /opt/ragforge

# Create production environment file
cp .env.production.example .env.production
nano .env.production
```

Set the following in `.env.production`:
```ini
ENVIRONMENT=production
ENABLE_AUTH=true
API_KEYS=your-strong-random-api-key-here
ALLOWED_ORIGINS=https://rag.yourdomain.com
GOOGLE_API_KEY=your_gemini_api_key_if_using_gemini
WORKERS=4
```

### Step 2: Build and Launch Containers
```bash
# Build and start services in background
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Verify running containers and health
docker compose ps
docker compose logs -f backend
```

### Step 3: Verify Health
```bash
curl http://localhost:8000/api/health
```

---

## 3. Strategy 2: Render.com (PaaS)

Render provides simple GitHub-connected deployments with persistent disk support.

### Step 1: Create a Web Service on Render
1. Connect your GitHub repository to [Render Dashboard](https://dashboard.render.com).
2. Choose **Web Service**.
3. Select **Docker** as the runtime.
4. Set **Dockerfile Path**: `./Dockerfile` (uses unified all-in-one image).

### Step 2: Configure Environment Variables
In the **Environment** tab on Render, add:
| Key | Value | Notes |
|-----|-------|-------|
| `PORT` | `8000` | Internal port |
| `ENVIRONMENT` | `production` | Enables production optimizations |
| `ENABLE_AUTH` | `false` or `true` | Enable API authentication |
| `API_KEYS` | `your-secret-api-key` | If auth is enabled |
| `GOOGLE_API_KEY` | `AIzaSy...` | Gemini API key for LLM responses |
| `WORKERS` | `2` | Number of Gunicorn worker threads |

### Step 3: Attach Persistent Disk
1. In the service settings, go to **Disks**.
2. Click **Add Disk**:
   - **Name**: `ragforge-storage`
   - **Mount Path**: `/app/storage`
   - **Size**: 5 GB to 20 GB (expandable anytime)
3. Deploy! Render will build the image, mount the disk, and provide a free `https://ragforge-xxxx.onrender.com` SSL domain.

---

## 4. Strategy 4: Decoupled Setup (Vercel + Cloud Backend)

Deploy the React frontend to Vercel's global edge network for maximum speed, and host the FastAPI backend on Render or Railway.

### Step 1: Deploy Backend (Render / Railway / VPS)
Deploy backend container and get the public backend URL (e.g. `https://api-ragforge.onrender.com`).

### Step 2: Configure Vercel Rewrites
In `react-frontend/`, add a `vercel.json` file:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api-ragforge.onrender.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Step 3: Deploy to Vercel
```bash
cd react-frontend
npm i -g vercel
vercel --prod
```

---

## 5. SSL / HTTPS Configuration (Nginx + Let's Encrypt)

If hosting on a VPS or bare-metal server, setup host Nginx reverse proxy with automated Certbot SSL certificates.

### Step 1: Install Nginx & Certbot
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Step 2: Create Nginx Site Configuration
Create `/etc/nginx/sites-available/ragforge`:
```nginx
server {
    server_name rag.yourdomain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:80;  # Points to frontend container
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ragforge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 3: Obtain Free SSL Certificate
```bash
sudo certbot --nginx -d rag.yourdomain.com
```

---

## 6. Backup & Disaster Recovery

### Automated Backup Script
Create `/opt/ragforge/scripts/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/ragforge"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

echo "Backing up RAGForge storage and documents..."
docker run --rm \
  --volumes-from ragforge-backend \
  -v "$BACKUP_DIR":/backup \
  alpine tar czf "/backup/ragforge_backup_$TIMESTAMP.tar.gz" /app/storage /app/data

# Keep only last 14 daily backups
find "$BACKUP_DIR" -type f -name "ragforge_backup_*.tar.gz" -mtime +14 -delete
echo "Backup complete: ragforge_backup_$TIMESTAMP.tar.gz"
```

Make executable and add to cron:
```bash
chmod +x /opt/ragforge/scripts/backup.sh
# Run daily at 2:00 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ragforge/scripts/backup.sh >> /var/log/ragforge_backup.log 2>&1") | crontab -
```

### Restoring from Backup
```bash
# Stop backend
docker compose stop backend

# Restore data
docker run --rm \
  --volumes-from ragforge-backend \
  -v "/opt/backups/ragforge":/backup \
  alpine sh -c "tar xzf /backup/ragforge_backup_YYYYMMDD_HHMMSS.tar.gz -C /"

# Restart backend
docker compose start backend
```

---

## 7. Production Security Checklist

Before making RAGForge publicly accessible:
- [ ] Set `ENABLE_AUTH=true` and configure strong `API_KEYS` in `.env.production`.
- [ ] Update `ALLOWED_ORIGINS` to only allow your trusted production domain names.
- [ ] Ensure HTTPS / SSL is active (via Let's Encrypt, Cloudflare, or PaaS SSL).
- [ ] Validate `/api/metrics` is protected by API key authentication.
- [ ] Verify maximum file upload size is enforced (default 50MB).
- [ ] Confirm persistent volume disks are properly mounted.
- [ ] Configure automatic daily backups for `/app/storage` and `/app/data`.
