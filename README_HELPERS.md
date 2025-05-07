# Ram Naam Jaap Development Helpers

This document explains the development helper scripts available in this project.

## Setup

The project uses:
- Python 3.12
- Django 5.0.2
- Virtual environment in the root folder
- PostgreSQL database

## Helper Scripts

### 1. `durga.py`

A comprehensive Python script for managing Django development tasks.

Usage:
```bash
python durga.py [command]
```

Available commands:
- `all`: Default command - clears cache, collects static files, and starts the development server
- `clearcache`: Clears Django cache and Python cache files
- `collectstatic`: Collects static files
- `runserver`: Starts the Django development server

Example:
```bash
# Clear cache only
python durga.py clearcache

# Collect static files only
python durga.py collectstatic

# Full development workflow (clear cache, collect static, run server)
python durga.py
# or
python durga.py all
```

### 2. `ramjaap.sh`

A shell script that provides a convenient interface for common project tasks.

Usage:
```bash
./ramjaap.sh [command]
```

Available commands:
- `start`: Clear cache, collect static files, and start the development server
- `test`: Run tests for the project
- `makemigr`: Create migrations for model changes
- `migrate`: Apply database migrations
- `collectstatic`: Collect static files
- `clearcache`: Clear Django and Python cache files
- `shell`: Start Django shell
- `createsuperuser`: Create a superuser
- `check`: Run Django system checks
- `help`: Show the help message

Example:
```bash
# Start development server
./ramjaap.sh start

# Run tests
./ramjaap.sh test

# Create migrations
./ramjaap.sh makemigr
```

## Project Structure

- `manage.py`: Django management command script in the root directory
- `durga.py`: Custom development helper script
- `ramjaap.sh`: Shell script for common operations
- `venv/`: Python virtual environment
- `ram_naam_jaap/`: Main project directory
  - `config/`: Project settings and configuration
  - `core/`: Core application with base views and templates
  - `accounts/`: User account management
  - `jaap/`: Jaap counting functionality
  - `dashboard/`: User dashboard
  - `community/`: Community features
  - `static/`: Static files (CSS, JS, images)
  - `staticfiles/`: Collected static files
  - `templates/`: HTML templates
  - `media/`: User-uploaded files

## URLs

- `/`: Home page
- `/admin/`: Custom admin dashboard
- `/durga/`: Django admin interface
- `/accounts/`: User authentication views
- `/jaap/`: Jaap counting functionality
- `/dashboard/`: User dashboard
- `/community/`: Community features

## Cache Busting

Static files are served with cache-busting URLs using a timestamp parameter, ensuring users always get the latest version of assets when files are updated.

## Development Tips

1. Always activate the virtual environment before working on the project:
   ```bash
   source venv/bin/activate
   ```

2. If you make changes to static files (CSS, JS), run:
   ```bash
   ./ramjaap.sh collectstatic
   ```

3. If you make changes to models, create and apply migrations:
   ```bash
   ./ramjaap.sh makemigr
   ./ramjaap.sh migrate
   ```

4. For a complete development setup with cache clearing, static collection, and server start:
   ```bash
   ./ramjaap.sh start
   ```

5. If changes aren't appearing in the browser:
   - Hard reload the page (Ctrl+Shift+R or Cmd+Shift+R)
   - Clear browser cache in developer tools
   - Try a private/incognito window 