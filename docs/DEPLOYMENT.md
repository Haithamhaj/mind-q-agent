# Mind-Q Production Deployment Guide

## 1. Prerequisites
- Docker & Docker Compose installed
- A domain name (e.g., `mind-q.com`)
- SSL Certificates (Let's Encrypt recommended)

## 2. Environment Setup
Create a `.env.prod` file:
```bash
DOMAIN_NAME=mind-q.com
API_URL=https://mind-q.com/api/v1
```

## 3. Docker Deployment
Run the production stack:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 4. Nginx & SSL Configuration
The `frontend` service uses a multi-stage Dockerfile that serves built assets via Nginx.
Ensure your `frontend/nginx.conf` looks typically like this for SSL:

```nginx
server {
    listen 80;
    server_name mind-q.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name mind-q.com;
    
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 5. Persistence
- **Database**: The SQLite database is volume-mounted at `./data`. Ensure regular backups of this directory.
- **n8n**: Workflow data is persisted in the `n8n_data` volume.

## 6. Monitoring
- View logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Check API health: `curl https://mind-q.com/api/v1/health`
