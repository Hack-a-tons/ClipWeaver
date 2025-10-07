# 🚀 ClipWeaver Deployment Guide

## Prerequisites

- Ubuntu server with Docker installed
- Docker Compose v2.x (using `docker compose` not `docker-compose`)
- Domain configured: `*.clip.hurated.com` pointing to your server
- Azure OpenAI account with GPT-4 Vision deployment

## 📋 Quick Start

### 1. Clone the Repository

```bash
cd /path/to/deployment
git clone <your-repo-url> ClipWeaver
cd ClipWeaver
```

### 2. Configure Environment Variables

Copy your working `.env` file to the project root:

```bash
cp /path/to/your/.env .env
```

Or create a new `.env` file based on `.env.example`:

```bash
cp .env.example .env
nano .env
```

Required variables:
```env
AZURE_OPENAI_ENDPOINT=https://sfo.openai.azure.com/
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
BACKEND_PORT=13000
BACKEND_HOST=0.0.0.0
FRONTEND_PORT=14000
```

### 3. Start Services

```bash
docker compose up -d
```

### 4. Check Status

```bash
docker compose ps
docker compose logs -f
```

### 5. Test the API

```bash
curl http://localhost:13000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "scene_detection": "operational",
    "ai_description": "operational",
    "storage": "operational"
  }
}
```

## 🔧 Configuration

### Port Configuration

The following ports are used (configured in `.env`):
- **Backend:** 13000 (default)
- **Frontend:** 14000 (default)

These ports are selected to avoid conflicts with existing services on your server.

### Domain Configuration

Update your nginx configuration to proxy requests:

```nginx
# Backend API
server {
    listen 80;
    server_name api.clip.hurated.com;
    
    location / {
        proxy_pass http://localhost:13000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for video processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        
        # Handle large video uploads
        client_max_body_size 500M;
    }
}

# Frontend App
server {
    listen 80;
    server_name app.clip.hurated.com;
    
    location / {
        proxy_pass http://localhost:14000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Reload nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Configuration (Optional but Recommended)

Use Let's Encrypt for SSL certificates:

```bash
sudo certbot --nginx -d api.clip.hurated.com -d app.clip.hurated.com
```

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Stop Services

```bash
docker compose down
```

### Rebuild After Code Changes

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Clean Up

```bash
# Stop and remove containers
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v

# Remove images
docker compose down --rmi all
```

## 📊 Monitoring

### Check Container Health

```bash
docker compose ps
```

### Resource Usage

```bash
docker stats
```

### Disk Space

```bash
du -sh output/
```

## 🐛 Troubleshooting

### Backend Not Starting

1. Check logs:
   ```bash
   docker compose logs backend
   ```

2. Verify environment variables:
   ```bash
   docker compose exec backend env | grep AZURE
   ```

3. Test Azure OpenAI connection:
   ```bash
   docker compose exec backend python -c "from openai import AzureOpenAI; print('OK')"
   ```

### Frontend Not Starting

1. Check logs:
   ```bash
   docker compose logs frontend
   ```

2. Verify node_modules are installed:
   ```bash
   docker compose exec frontend ls node_modules
   ```

### Port Already in Use

If you get a port conflict, update the ports in `.env`:

```env
BACKEND_PORT=15000
FRONTEND_PORT=16000
```

Then restart:
```bash
docker compose down
docker compose up -d
```

### Video Processing Fails

1. Check ffmpeg is available:
   ```bash
   docker compose exec backend ffmpeg -version
   ```

2. Check disk space:
   ```bash
   df -h
   ```

3. Test with a small video first (< 10MB)

### Azure OpenAI Errors

1. Verify credentials:
   ```bash
   curl -H "api-key: $AZURE_OPENAI_KEY" "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=$AZURE_OPENAI_API_VERSION"
   ```

2. Check deployment name matches your Azure resource

3. Ensure your deployment supports vision capabilities

## 🔄 Updates

### Pull Latest Changes

```bash
git pull
docker compose down
docker compose build
docker compose up -d
```

### Update Dependencies

Backend:
```bash
docker compose exec backend pip install --upgrade -r requirements.txt
```

Frontend:
```bash
docker compose exec frontend npm update
```

## 📦 Backup

### Backup Configuration

```bash
tar -czf clipweaver-backup-$(date +%Y%m%d).tar.gz \
  .env \
  output/ \
  backend/ \
  frontend/
```

### Restore from Backup

```bash
tar -xzf clipweaver-backup-YYYYMMDD.tar.gz
docker compose up -d
```

## 🔒 Security Notes

1. **Never commit `.env` to git** - It contains sensitive API keys
2. **Use SSL in production** - Configure certbot for HTTPS
3. **Firewall rules** - Only expose necessary ports (80, 443)
4. **Regular updates** - Keep Docker images and dependencies updated
5. **API rate limiting** - Consider adding rate limiting in nginx

## 📈 Performance Tuning

### Increase Worker Processes

Edit `backend/app.py` to use gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:13000 app:app
```

### Optimize Video Processing

Adjust scene detection threshold in `.env`:

```env
DEFAULT_SCENE_THRESHOLD=0.5
```

### Cache Configuration

Add Redis for caching (optional):

```yaml
# Add to compose.yml
redis:
  image: redis:7-alpine
  container_name: clipweaver-redis
  ports:
    - "6379:6379"
  networks:
    - clipweaver-network
```

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/dbystruev/ClipWeaver/issues)
- Email: support@hurated.com

## 📄 License

MIT License © 2025 Denis Bystruev, Valerii Egorov
