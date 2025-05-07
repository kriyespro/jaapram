# Ram Naam Jaap - Deployment Guide

This guide provides instructions for deploying the Ram Naam Jaap application to a production server.

## Prerequisites

- Ubuntu 20.04 or later server
- Python 3.12 installed
- PostgreSQL
- Redis
- Nginx
- Supervisor
- Let's Encrypt SSL certificate

## Server Setup

### Update System and Install Dependencies

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3.12-dev postgresql postgresql-contrib nginx supervisor redis-server git certbot python3-certbot-nginx
```

### Setup PostgreSQL

```bash
sudo -u postgres psql
```

In PostgreSQL shell:

```sql
CREATE DATABASE ram_naam_jaap_db;
CREATE USER ram_naam_jaap_user WITH ENCRYPTED PASSWORD 'strong-production-password-change-me';
GRANT ALL PRIVILEGES ON DATABASE ram_naam_jaap_db TO ram_naam_jaap_user;
\q
```

### Configure Nginx

1. Copy the provided nginx.txt configuration to the server:

```bash
sudo cp /path/to/nginx.txt /etc/nginx/sites-available/ram-naam-jaap
```

2. Create a symbolic link to enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/ram-naam-jaap /etc/nginx/sites-enabled/
```

3. Test configuration and restart Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Setup SSL with Let's Encrypt

```bash
sudo certbot --nginx -d ram-naam-jaap.example.com -d www.ram-naam-jaap.example.com
```

## Application Deployment

### Setup Directories and Permissions

```bash
sudo mkdir -p /var/www/ram-naam-jaap/static /var/www/ram-naam-jaap/media
sudo mkdir -p /var/log/ram-naam-jaap
sudo chown -R $USER:$USER /var/www/ram-naam-jaap
sudo chown -R $USER:$USER /var/log/ram-naam-jaap
```

### Clone the Repository

```bash
cd ~
git clone https://github.com/your-username/ram-naam-jaap.git
cd ram-naam-jaap
```

### Setup Python Environment and Dependencies

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configure Environment Variables

Copy the production environment file:

```bash
cp .env-pro .env
```

Edit the .env file to update settings like SECRET_KEY, database credentials, and other configuration values.

### Database Setup

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### Configure Supervisor

1. Copy the supervisor configuration file:

```bash
sudo cp ram_naam_jaap.conf /etc/supervisor/conf.d/
```

2. Update the supervisor configuration:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ram_naam_jaap
sudo supervisorctl start ram_naam_jaap_celery
sudo supervisorctl start ram_naam_jaap_celery_beat
```

### Verify Deployment

Visit your domain (https://ram-naam-jaap.example.com) to ensure the application is running properly.

Check the logs if you encounter any issues:

```bash
# Application logs
sudo tail -f /var/log/ram-naam-jaap/gunicorn.log

# Celery logs
sudo tail -f /var/log/ram-naam-jaap/celery.log
sudo tail -f /var/log/ram-naam-jaap/celery_beat.log

# Nginx logs
sudo tail -f /var/log/nginx/ram-naam-jaap.access.log
sudo tail -f /var/log/nginx/ram-naam-jaap.error.log
```

## Using GitHub Actions for Automated Deployment

The repository includes a GitHub Actions workflow for automated deployment. To use it:

1. Add the following secrets to your GitHub repository:
   - `SSH_PRIVATE_KEY`: Your server's SSH private key
   - `SSH_KNOWN_HOSTS`: Output of `ssh-keyscan <server-ip>`
   - `SERVER_IP`: Your server's IP address
   - `SSH_USER`: Your server's username
   - `SLACK_WEBHOOK`: (Optional) Slack webhook URL for deployment notifications

2. Push to the main branch to trigger a deployment.

## Maintenance

### Updating the Application

To update the application manually:

```bash
cd ~/ram_naam_jaap
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo supervisorctl restart ram_naam_jaap
sudo supervisorctl restart ram_naam_jaap_celery
sudo supervisorctl restart ram_naam_jaap_celery_beat
```

### Backup Database

```bash
pg_dump -U ram_naam_jaap_user ram_naam_jaap_db > backup-$(date +%Y%m%d).sql
```

### Restore Database

```bash
psql -U ram_naam_jaap_user ram_naam_jaap_db < backup-filename.sql
``` 