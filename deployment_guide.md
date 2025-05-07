# JaapRam Deployment Guide for Nginx + PostgreSQL

This guide provides detailed instructions for deploying the JaapRam application using Nginx, Gunicorn, and PostgreSQL on a production server, including specifics for hosting multiple apps on the same Nginx server.

## Prerequisites

- Linux server (Ubuntu/Debian recommended)
- Git 
- Python 3.12 installed
- PostgreSQL installed and running
- Nginx installed
- Redis server installed (optional but recommended)
- Domain name with DNS configured

## 1. Clone the Repository

```bash
# Create a directory for the application
mkdir -p /var/www/jaapram
cd /var/www/jaapram

# Clone the repository
git clone https://github.com/your-username/sd-dj-ramjaap2-pro.git .
```

## 2. Set Up Virtual Environment

```bash
# Create a virtual environment
python3.12 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r ram_naam_jaap/requirements.txt
```

## 3. Configure PostgreSQL

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE jaapram;
CREATE USER jaapram_user WITH PASSWORD 'strong_password_here';
ALTER ROLE jaapram_user SET client_encoding TO 'utf8';
ALTER ROLE jaapram_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jaapram_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jaapram TO jaapram_user;
\q
```

## 4. Environment Configuration

Create an environment file to store your settings:

```bash
cd /var/www/jaapram
nano .env
```

Add the following environment variables:

```
DJANGO_ENV=production
SECRET_KEY=your_secure_secret_key_here
DATABASE_URL=postgres://jaapram_user:strong_password_here@localhost:5432/jaapram
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
REDIS_URL=redis://localhost:6379/1
ADMIN_URL=durga/
DASHBOARD_URL=admin/
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## 5. Deploy Static Files

```bash
cd /var/www/jaapram
source venv/bin/activate
cd ram_naam_jaap

# Collect static files
python manage.py collectstatic --no-input
```

## 6. Run Migrations and Create Superuser

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 7. Set Up Gunicorn

Create a systemd service file to manage Gunicorn:

```bash
sudo nano /etc/systemd/system/jaapram.service
```

Add the following configuration:

```ini
[Unit]
Description=JaapRam Gunicorn daemon
After=network.target postgresql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/jaapram/ram_naam_jaap
ExecStart=/var/www/jaapram/venv/bin/gunicorn config.wsgi:application --workers 3 --bind 127.0.0.1:8001 --timeout 120 --error-logfile /var/log/gunicorn/jaapram-error.log --access-logfile /var/log/gunicorn/jaapram-access.log
Restart=on-failure
Environment="DJANGO_ENV=production"
EnvironmentFile=/var/www/jaapram/.env

[Install]
WantedBy=multi-user.target
```

Make sure log directories exist:

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

Start and enable the service:

```bash
sudo systemctl start jaapram
sudo systemctl enable jaapram
sudo systemctl status jaapram
```

## 8. Configure Nginx for Multiple Apps

Since your Nginx server hosts multiple applications, we'll create a separate server block for JaapRam:

```bash
sudo nano /etc/nginx/sites-available/jaapram
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com https://cdnjs.cloudflare.com";

    # Client max body size
    client_max_body_size 10M;

    # Path for static files
    root /var/www/jaapram/ram_naam_jaap/staticfiles;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    # Static files
    location /static/ {
        alias /var/www/jaapram/ram_naam_jaap/staticfiles/;
        expires 30d;
        access_log off;
    }

    # Media files
    location /media/ {
        alias /var/www/jaapram/ram_naam_jaap/media/;
        expires 30d;
    }

    # Proxy requests to Gunicorn
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8001;
        proxy_redirect off;
        proxy_buffering off;
        proxy_read_timeout 120s;
    }

    # Error handling
    error_page 404 /404.html;
    error_page 500 502 503 504 /500.html;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/jaapram /etc/nginx/sites-enabled/
sudo nginx -t  # Test Nginx configuration
sudo systemctl restart nginx
```

## 9. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 10. Redis and Celery Setup (Optional but Recommended)

Create a systemd service for Celery worker:

```bash
sudo nano /etc/systemd/system/jaapram-celery.service
```

Add the following:

```ini
[Unit]
Description=JaapRam Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/jaapram/ram_naam_jaap
ExecStart=/var/www/jaapram/venv/bin/celery -A config worker -l INFO
Restart=on-failure
Environment="DJANGO_ENV=production"
EnvironmentFile=/var/www/jaapram/.env

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start jaapram-celery
sudo systemctl enable jaapram-celery
```

Create a systemd service for Celery beat (for scheduled tasks):

```bash
sudo nano /etc/systemd/system/jaapram-celerybeat.service
```

Add the following:

```ini
[Unit]
Description=JaapRam Celery Beat
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/jaapram/ram_naam_jaap
ExecStart=/var/www/jaapram/venv/bin/celery -A config beat -l INFO
Restart=on-failure
Environment="DJANGO_ENV=production"
EnvironmentFile=/var/www/jaapram/.env

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start jaapram-celerybeat
sudo systemctl enable jaapram-celerybeat
```

## 11. Setup Automatic Database Backups

Create a backup script:

```bash
sudo nano /var/www/jaapram/backup.sh
```

Add the following:

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/var/backups/jaapram"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U jaapram_user jaapram | gzip > "$BACKUP_DIR/jaapram_db_$DATE.sql.gz"

# Media files backup
tar -czf "$BACKUP_DIR/jaapram_media_$DATE.tar.gz" /var/www/jaapram/ram_naam_jaap/media

# Keep only the last 7 backups
find $BACKUP_DIR -name "jaapram_db_*.sql.gz" -type f -mtime +7 -delete
find $BACKUP_DIR -name "jaapram_media_*.tar.gz" -type f -mtime +7 -delete
```

Make the script executable:

```bash
sudo chmod +x /var/www/jaapram/backup.sh
```

Create a cron job to run daily backups:

```bash
sudo crontab -e
```

Add the following line:

```
0 2 * * * /var/www/jaapram/backup.sh
```

## 12. Maintenance

### Deploying Updates

```bash
cd /var/www/jaapram
git pull
source venv/bin/activate
cd ram_naam_jaap
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart jaapram
```

### Monitoring Logs

```bash
# Application logs
sudo tail -f /var/log/gunicorn/jaapram-error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Celery logs
sudo journalctl -u jaapram-celery -f
sudo journalctl -u jaapram-celerybeat -f
```

## Troubleshooting

### Application Not Responding

1. Check if the Gunicorn service is running:
   ```bash
   sudo systemctl status jaapram
   ```

2. Check application logs:
   ```bash
   sudo tail -f /var/log/gunicorn/jaapram-error.log
   ```

3. Check Nginx logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check database connection parameters in `.env` file.

3. Manually test database connection:
   ```bash
   psql postgres://jaapram_user:password@localhost:5432/jaapram
   ```

### Static Files Not Found

1. Check if static files were collected properly:
   ```bash
   ls -la /var/www/jaapram/ram_naam_jaap/staticfiles
   ```

2. Verify Nginx configuration paths are correct.

3. Ensure file permissions are set correctly:
   ```bash
   sudo chown -R www-data:www-data /var/www/jaapram
   ```

## Security Considerations

1. Regularly update your system:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. Configure a firewall:
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

3. Set up automatic security updates:
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure unattended-upgrades
   ```

4. Regularly check for vulnerable dependencies:
   ```bash
   pip install safety
   safety check -r ram_naam_jaap/requirements.txt
   ```

5. Monitor system logs for suspicious activity:
   ```bash
   sudo journalctl -f
   ``` 