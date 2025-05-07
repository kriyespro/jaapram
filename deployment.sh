#!/bin/bash

# Ram Naam Jaap Multi-App Deployment Script
# This script automates the deployment of multiple Django applications for ramjaap.in

# Color configuration for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Application settings - MODIFY THESE VARIABLES
# Main domain
DOMAIN="ramjaap.in"
# Primary application settings
PRIMARY_APP_NAME="ram_naam_jaap"
# User that will run the application
APP_USER="appuser"
# Base path for all applications
BASE_PATH="/var/www/$DOMAIN"
# Virtual environment path
VENV_PATH="$BASE_PATH/venv"
# Git repository for main application
GIT_REPO_URL="https://github.com/yourusername/ram-naam-jaap.git"
# Admin email for Let's Encrypt
ADMIN_EMAIL="admin@ramjaap.in"

# Secondary applications
declare -A APPS=(
  ["ram_naam_jaap"]="/"
  ["blog"]="/blog"
  ["meditation"]="/meditation"
)

# Database settings
DB_NAME="ramjaap_db"
DB_USER="ramjaap_user"
DB_PASSWORD="change_this_password"

# Functions
print_message() {
  local color=$1
  local message=$2
  echo -e "${color}${message}${NC}"
}

check_root() {
  if [ "$(id -u)" != "0" ]; then
    print_message "$RED" "This script must be run as root" 1>&2
    exit 1
  fi
}

# Check if running as root
check_root

# Start deployment
print_message "$CYAN" "==================================================="
print_message "$CYAN" "  Ram Naam Jaap Multi-App Deployment"
print_message "$CYAN" "==================================================="
print_message "$GREEN" "Starting deployment for domain: $DOMAIN"

# Update system packages
print_message "$YELLOW" "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_message "$YELLOW" "Installing dependencies..."
apt install -y python3 python3-venv python3-dev nginx git supervisor postgresql postgresql-contrib libpq-dev build-essential certbot python3-certbot-nginx memcached

# Create application user if it doesn't exist
if ! id "$APP_USER" &>/dev/null; then
  print_message "$YELLOW" "Creating application user: $APP_USER"
  useradd -m -s /bin/bash "$APP_USER"
fi

# Create application directories
print_message "$YELLOW" "Creating application directories..."
mkdir -p "$BASE_PATH"
mkdir -p "$BASE_PATH/logs"
mkdir -p "$BASE_PATH/static"
mkdir -p "$BASE_PATH/media"
mkdir -p "$BASE_PATH/shared/templates"
mkdir -p "$BASE_PATH/shared/static"
mkdir -p "$BASE_PATH/shared/utils"

# Clone or update repositories
for app in "${!APPS[@]}"; do
  APP_DIR="$BASE_PATH/$app"
  print_message "$YELLOW" "Setting up application: $app"
  
  if [ -d "$APP_DIR/.git" ]; then
    print_message "$GREEN" "Updating existing repository for $app..."
    cd "$APP_DIR"
    git pull
  else
    print_message "$GREEN" "Cloning repository for $app..."
    # Note: In a real scenario, each app would have its own repository URL
    if [ "$app" == "$PRIMARY_APP_NAME" ]; then
      git clone "$GIT_REPO_URL" "$APP_DIR"
    else
      # For demonstration, we're using placeholders for other app repos
      print_message "$YELLOW" "Placeholder: Clone repository for $app"
      mkdir -p "$APP_DIR"
      echo "# $app Django application" > "$APP_DIR/README.md"
    fi
  fi
done

# Set up shared components
print_message "$YELLOW" "Setting up shared components..."
# Create a shared settings file
cat > "$BASE_PATH/shared/shared_settings.py" << EOF
import os
from pathlib import Path

# Base paths
BASE_DIR = Path('$BASE_PATH')
SHARED_DIR = BASE_DIR / 'shared'

# Common settings
DEBUG = False
ALLOWED_HOSTS = ['$DOMAIN', 'www.$DOMAIN', 'blog.$DOMAIN', 'meditation.$DOMAIN']

# Security settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-key-for-production-only')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database settings (shared database)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', '$DB_NAME'),
        'USER': os.environ.get('DB_USER', '$DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '$DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static and media settings
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Additional shared static directories for development
STATICFILES_DIRS = [
    SHARED_DIR / 'static',
]

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'noreply@$DOMAIN'
EOF

# Set up virtual environment and install dependencies
print_message "$YELLOW" "Setting up Python virtual environment and installing dependencies..."
if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

for app in "${!APPS[@]}"; do
  APP_DIR="$BASE_PATH/$app"
  if [ -f "$APP_DIR/requirements.txt" ]; then
    print_message "$GREEN" "Installing Python dependencies for $app..."
    pip install -r "$APP_DIR/requirements.txt"
  fi
done

# Install additional common packages
print_message "$GREEN" "Installing common Python packages..."
pip install gunicorn psycopg2-binary django==5.0.2 jinja2 pyjwt pymemcache

# Create a script to manage all applications
print_message "$YELLOW" "Creating management script..."
cat > "$BASE_PATH/manage_all.sh" << 'EOF'
#!/bin/bash
source venv/bin/activate

APPS=("ram_naam_jaap" "blog" "meditation")
ACTION=$1
PARAMS=${@:2}

function run_command() {
    local app=$1
    local cmd=$2
    local params=$3
    echo "Running '$cmd $params' for $app..."
    cd "/var/www/ramjaap.in/$app"
    python manage.py $cmd $params
    echo "Done with $app"
    echo "-------------------"
}

for app in "${APPS[@]}"; do
    run_command $app $ACTION "$PARAMS"
done

echo "All operations completed!"
EOF

chmod +x "$BASE_PATH/manage_all.sh"

# Create .env file for environment variables
print_message "$YELLOW" "Creating .env file..."
cat > "$BASE_PATH/.env" << EOF
DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DJANGO_SETTINGS_MODULE=ram_naam_jaap.settings
EOF

# Set up PostgreSQL database
print_message "$YELLOW" "Setting up PostgreSQL database..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  print_message "$GREEN" "Database $DB_NAME already exists."
else
  print_message "$GREEN" "Creating database $DB_NAME..."
  sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
  sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
  sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
  sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
  sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
  sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
fi

# Configure and run migrations for each application
for app in "${!APPS[@]}"; do
  APP_DIR="$BASE_PATH/$app"
  print_message "$YELLOW" "Running migrations for $app..."
  
  if [ -f "$APP_DIR/manage.py" ]; then
    cd "$APP_DIR"
    python manage.py migrate
  else
    print_message "$RED" "No manage.py found for $app, skipping migrations"
  fi
done

# Collect static files
print_message "$YELLOW" "Collecting static files..."
cd "$BASE_PATH/$PRIMARY_APP_NAME"
python manage.py collectstatic --noinput --clear

# Setup Supervisor configuration for all apps
print_message "$YELLOW" "Setting up Supervisor configuration..."
cat > "/etc/supervisor/conf.d/ramjaap.conf" << EOF
[group:ramjaap]
programs=$(echo "${!APPS[@]}" | tr ' ' ',')

EOF

# Add configuration for each app
for app in "${!APPS[@]}"; do
  cat >> "/etc/supervisor/conf.d/ramjaap.conf" << EOF
[program:$app]
command=$VENV_PATH/bin/gunicorn --workers 3 --bind unix:$BASE_PATH/$app.sock ${app}.wsgi:application
directory=$BASE_PATH/$app
user=$APP_USER
autostart=true
autorestart=true
environment=DJANGO_SETTINGS_MODULE="${app}.settings"

EOF
done

# Restart Supervisor
print_message "$YELLOW" "Restarting Supervisor..."
supervisorctl reread
supervisorctl update
supervisorctl restart all

# Setup Nginx configuration
print_message "$YELLOW" "Setting up Nginx configuration..."
cat > "/etc/nginx/sites-available/$DOMAIN" << EOF
# Main server block for the primary domain
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL configuration will be added by Certbot
    
    # Main application
    location / {
        proxy_pass http://unix:$BASE_PATH/ram_naam_jaap.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static and media files for all applications
    location /static/ {
        alias $BASE_PATH/static/;
        expires 30d;
    }
    
    location /media/ {
        alias $BASE_PATH/media/;
        expires 30d;
    }

    # Custom admin URL
    location /durga/ {
        proxy_pass http://unix:$BASE_PATH/ram_naam_jaap.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Add server blocks for subdomains
for app in "${!APPS[@]}"; do
  if [ "$app" != "$PRIMARY_APP_NAME" ]; then
    cat >> "/etc/nginx/sites-available/$DOMAIN" << EOF

# $app subdomain
server {
    listen 443 ssl http2;
    server_name ${app}.$DOMAIN;
    
    # SSL configuration will be added by Certbot
    
    # $app application
    location / {
        proxy_pass http://unix:$BASE_PATH/$app.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Use the same static and media files as the main domain
    location /static/ {
        alias $BASE_PATH/static/;
        expires 30d;
    }
    
    location /media/ {
        alias $BASE_PATH/media/;
        expires 30d;
    }
}
EOF
  fi
done

# Add HTTP to HTTPS redirect
cat >> "/etc/nginx/sites-available/$DOMAIN" << EOF

# HTTP to HTTPS redirect for all domains
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $(echo "${!APPS[@]}" | sed "s/ / $DOMAIN /g").$DOMAIN;
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF

# Enable the site
if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
  ln -s "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
fi

# Remove default site if exists
if [ -L "/etc/nginx/sites-enabled/default" ]; then
  rm "/etc/nginx/sites-enabled/default"
fi

# Set proper permissions
print_message "$YELLOW" "Setting proper permissions..."
chown -R "$APP_USER:$APP_USER" "$BASE_PATH"
chmod -R 755 "$BASE_PATH"

# Test Nginx configuration
print_message "$YELLOW" "Testing Nginx configuration..."
nginx -t

# Restart Nginx
print_message "$YELLOW" "Restarting Nginx..."
systemctl restart nginx

# Check if Nginx is active
if systemctl is-active --quiet nginx; then
  print_message "$GREEN" "Nginx is running."
else
  print_message "$RED" "Nginx failed to start. Check the configuration."
  exit 1
fi

# Set up SSL with Let's Encrypt
print_message "$YELLOW" "Setting up SSL with Let's Encrypt..."
# Build domain parameters for certbot
DOMAIN_PARAMS="-d $DOMAIN -d www.$DOMAIN"
for app in "${!APPS[@]}"; do
  if [ "$app" != "$PRIMARY_APP_NAME" ]; then
    DOMAIN_PARAMS="$DOMAIN_PARAMS -d ${app}.$DOMAIN"
  fi
done

certbot --nginx $DOMAIN_PARAMS --non-interactive --agree-tos --email "$ADMIN_EMAIL"

# Set up automatic renewal
print_message "$YELLOW" "Setting up automatic SSL renewal..."
if ! crontab -l | grep -q certbot; then
  (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
fi

# Final message
print_message "$GREEN" "==================================================="
print_message "$GREEN" "  Deployment Completed Successfully!"
print_message "$GREEN" "==================================================="
print_message "$CYAN" "Your applications are now available at:"
print_message "$CYAN" "  Main application: https://$DOMAIN"
for app in "${!APPS[@]}"; do
  if [ "$app" != "$PRIMARY_APP_NAME" ]; then
    print_message "$CYAN" "  $app: https://${app}.$DOMAIN"
  fi
done
print_message "$CYAN" "Admin interface: https://$DOMAIN/durga/"
print_message "$YELLOW" "Remember to change the default superuser password!"
print_message "$YELLOW" "Ensure your DNS records are properly configured for all domains and subdomains."
print_message "$GREEN" "Thank you for using the Ram Naam Jaap Multi-App Deployment script!"

# Exit with success
exit 0 