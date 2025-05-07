#!/usr/bin/env python
"""
Fresh start script - clears all caches and starts development server
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
import django
django.setup()

from django.core.cache import cache
from django.core.management import call_command


def clear_django_cache():
    """Clear the Django cache"""
    print("Clearing Django cache...")
    cache.clear()
    print("✅ Django cache cleared")


def clear_pyc_files():
    """Clear compiled Python files"""
    print("Clearing .pyc files...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    # Clear __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
    
    print("✅ Compiled Python files cleared")


def clear_redis_cache():
    """Try to clear Redis cache if it's available"""
    try:
        import redis
        from django.conf import settings
        
        print("Clearing Redis cache...")
        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.flushall()
        print("✅ Redis cache cleared")
        return True
    except (ImportError, redis.exceptions.ConnectionError, AttributeError):
        print("⚠️ Could not clear Redis cache - either Redis is not installed or not running")
        return False


def run_server():
    """Run the Django development server"""
    print("\n🚀 Starting Django development server...\n")
    call_command('runserver')


def flush_sessions():
    """Flush Django sessions"""
    print("Flushing Django sessions...")
    call_command('clearsessions')
    print("✅ Django sessions cleared")


def collect_static():
    """Collect static files"""
    print("Collecting static files...")
    call_command('collectstatic', interactive=False, verbosity=0)
    print("✅ Static files collected")


def restart_server():
    """Use runserver with restart option"""
    print("\n🔄 Starting Django development server with auto-reload...\n")
    subprocess.run(['python', 'manage.py', 'runserver', '--noreload'])


if __name__ == "__main__":
    # Parse command line arguments
    run_dev_server = True
    collect_statics = False
    
    if len(sys.argv) > 1:
        if 'nostatic' in sys.argv:
            collect_statics = False
        if 'static' in sys.argv:
            collect_statics = True
        if 'noserver' in sys.argv:
            run_dev_server = False
    
    # Run all cleaning operations
    clear_django_cache()
    clear_pyc_files()
    clear_redis_cache()
    flush_sessions()
    
    # Optionally collect static files
    if collect_statics:
        collect_static()
    
    print("\n✨ All caches cleared successfully! ✨\n")
    
    # Run development server if requested
    if run_dev_server:
        run_server() 