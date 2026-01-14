# PassAudit Deployment Guide

## Docker Deployment

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/botchx86/PassAudit.git
   cd PassAudit
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   nano .env
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Access the web interface:**
   - Open your browser to: http://localhost:5000

### Building Docker Image

Build the Docker image manually:

```bash
docker build -t passaudit:latest .
```

Run the container:

```bash
docker run -d \
  --name passaudit \
  -p 5000:5000 \
  -e SECRET_KEY="your-secret-key" \
  -v passaudit_data:/root/.passaudit \
  passaudit:latest
```

### Docker Compose Configuration

The `docker-compose.yml` file includes:
- **PassAudit service**: Web application
- **Volume**: Persistent storage for cache and config
- **Health check**: Automatic container health monitoring
- **Restart policy**: Automatic restart on failure

### Environment Variables

Key environment variables (see `.env.example` for all options):

- `SECRET_KEY`: Flask secret key (required in production)
- `PORT`: Port to bind to (default: 5000)
- `FLASK_ENV`: Flask environment (production/development)
- `HIBP_CHECK_ENABLED`: Enable HIBP breach checking (true/false)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Production Deployment

#### Using Nginx Reverse Proxy

1. **Uncomment Nginx service** in `docker-compose.yml`

2. **Create nginx.conf:**
   ```nginx
   server {
       listen 80;
       server_name passaudit.example.com;

       location / {
           proxy_pass http://passaudit:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Add SSL with Let's Encrypt:**
   ```bash
   docker run --rm \
     -v /etc/letsencrypt:/etc/letsencrypt \
     -v /var/www/certbot:/var/www/certbot \
     certbot/certbot certonly \
     --webroot -w /var/www/certbot \
     -d passaudit.example.com
   ```

#### Security Best Practices

1. **Change default secret key:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Enable HTTPS:**
   - Set `SESSION_COOKIE_SECURE=true`
   - Use Nginx with SSL certificates

3. **Restrict network access:**
   - Use firewall rules
   - Limit exposed ports
   - Use Docker networks for service isolation

4. **Enable rate limiting:**
   - Configure in `.env`
   - Use Nginx rate limiting

5. **Regular updates:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

### Kubernetes Deployment

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: passaudit
spec:
  replicas: 3
  selector:
    matchLabels:
      app: passaudit
  template:
    metadata:
      labels:
        app: passaudit
    spec:
      containers:
      - name: passaudit
        image: passaudit:latest
        ports:
        - containerPort: 5000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: passaudit-secrets
              key: secret-key
        volumeMounts:
        - name: passaudit-data
          mountPath: /root/.passaudit
      volumes:
      - name: passaudit-data
        persistentVolumeClaim:
          claimName: passaudit-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: passaudit
spec:
  selector:
    app: passaudit
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Managing Containers

**View logs:**
```bash
docker-compose logs -f passaudit
```

**Restart service:**
```bash
docker-compose restart passaudit
```

**Stop and remove:**
```bash
docker-compose down
```

**Update to latest version:**
```bash
git pull
docker-compose up -d --build
```

**Backup data:**
```bash
docker run --rm \
  -v passaudit_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/passaudit-backup-$(date +%Y%m%d).tar.gz /data
```

**Restore data:**
```bash
docker run --rm \
  -v passaudit_data:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/passaudit-backup-YYYYMMDD.tar.gz --strip 1"
```

## Traditional Deployment

### System Requirements

- Python 3.9+
- pip package manager
- 512MB RAM minimum (2GB+ recommended for batch processing)
- 100MB disk space

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download password database:**
   ```bash
   python scripts/download_passwords.py
   ```

3. **Initialize configuration:**
   ```bash
   python Main.py --config-init
   ```

### Running the Web Server

**Development:**
```bash
python run_web.py --debug
```

**Production with Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 'web.app:create_app()'
```

**Production with Waitress (Windows):**
```bash
waitress-serve --host=0.0.0.0 --port=5000 web.app:create_app
```

### Systemd Service (Linux)

Create `/etc/systemd/system/passaudit.service`:

```ini
[Unit]
Description=PassAudit Web Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/passaudit
Environment="PATH=/opt/passaudit/venv/bin"
ExecStart=/opt/passaudit/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 'web.app:create_app()'
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable passaudit
sudo systemctl start passaudit
```

## Monitoring

### Health Checks

The application provides a health check endpoint:
```bash
curl http://localhost:5000/
```

### Logs

**Docker logs:**
```bash
docker logs passaudit
```

**Application logs:**
```bash
tail -f ~/.passaudit/logs/passaudit.log
```

### Metrics

For production monitoring, consider integrating:
- Prometheus for metrics
- Grafana for visualization
- ELK stack for log aggregation

## Troubleshooting

**Container won't start:**
- Check logs: `docker logs passaudit`
- Verify port is available: `netstat -tulpn | grep 5000`
- Check permissions on volume mounts

**Cannot connect to web interface:**
- Verify container is running: `docker ps`
- Check firewall rules
- Verify port mapping in docker-compose.yml

**High memory usage:**
- Reduce `BATCH_PROCESSING_THREADS` in .env
- Limit `MAX_BATCH_SIZE` for large file uploads
- Increase container memory limits

**Database not loading:**
- Run: `python scripts/download_passwords.py --force`
- Check network connectivity
- Verify disk space

## Support

For issues and questions:
- GitHub Issues: https://github.com/botchx86/PassAudit/issues
- Documentation: https://github.com/botchx86/PassAudit

## License

MIT License - See LICENSE file for details
