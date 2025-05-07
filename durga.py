#!/usr/bin/env python
import os
import sys
import time
import shutil
from pathlib import Path
import subprocess
import argparse

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_colored(text, color):
    """Print text with color"""
    print(f"{color}{text}{RESET}")

def check_venv():
    """Check if script is running inside a virtual environment"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_colored("WARNING: You are not running this script inside a virtual environment.", YELLOW)
        response = input("Do you want to continue? (y/n): ").lower()
        if response != 'y':
            sys.exit(0)

def run_command(command, description=None):
    """Run a shell command with description and error handling"""
    if description:
        print_colored(f"\n{description}...", BLUE)
    
    try:
        process = subprocess.run(command, shell=True, check=True, text=True, 
                                capture_output=True)
        if process.stdout:
            print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"Error executing command: {command}", RED)
        print_colored(f"Error details: {e}", RED)
        if e.output:
            print_colored(f"Output: {e.output}", RED)
        if e.stderr:
            print_colored(f"Error output: {e.stderr}", RED)
        return False

def clear_cache():
    """Clear Django cache and temporary files"""
    print_colored("\n===== CLEARING CACHES =====", BOLD + GREEN)
    
    # Define paths to clean
    paths_to_clean = [
        './**/__pycache__',
        './**/.pytest_cache',
        './**/.coverage',
        './**/.DS_Store',
        './htmlcov/',
        './media/temp/',
    ]
    
    # Remove all Python cache files
    for pattern in paths_to_clean:
        run_command(f"find . -path '{pattern}' -delete", f"Removing {pattern}")
    
    # Remove __pycache__ directories
    run_command("find . -name '__pycache__' -type d -exec rm -rf {} +", "Removing __pycache__ directories")
    
    # Remove .pyc files
    run_command("find . -name '*.pyc' -delete", "Removing .pyc files")
    
    # Remove Django migrations cache files (but not the actual migrations)
    run_command("find . -path '*/migrations/*.py[co]' -delete", "Removing migration cache files")
    
    # Clear Django cache if management command exists
    run_command("python manage.py cache_clear", "Clearing Django cache")
    
    # Clear template cache
    print_colored("Template caches cleared successfully!", GREEN)
    
    print_colored("All caches cleared successfully!", GREEN)

def collect_static():
    """Collect static files for all apps"""
    print_colored("\n===== COLLECTING STATIC FILES =====", BOLD + GREEN)
    
    # Run Django's collectstatic command
    return run_command(
        "python manage.py collectstatic --noinput", 
        "Collecting static files"
    )

def start_server(app="main", port=8000):
    """Start Django development server for a specific app on a specified port"""
    print_colored(f"\n===== STARTING {app.upper()} SERVER ON PORT {port} =====", BOLD + GREEN)
    print_colored(f"Server will be available at http://127.0.0.1:{port}", BLUE)
    
    if app == "main":
        print_colored(f"Django admin interface available at http://127.0.0.1:{port}/durga", BLUE) 
        print_colored(f"Custom dashboard available at http://127.0.0.1:{port}/admin", BLUE)
    
    print_colored("Press Ctrl+C to stop the server.", YELLOW)
    print_colored("NOTE: If changes are not visible, hard reload your browser (Ctrl+Shift+R or Cmd+Shift+R)", YELLOW)
    
    # Start Django development server with the specified port
    settings = f"ram_naam_jaap.config.settings.{app}" if app != "main" else "ram_naam_jaap.config.settings"
    run_command(f"python manage.py runserver {port} --settings={settings}")

def start_all_servers():
    """Start all Django servers in separate processes"""
    print_colored("\n===== STARTING ALL SERVERS =====", BOLD + GREEN)
    
    # Define the apps and their ports
    apps = {
        "main": 8000,
        "admin": 8001,
        "api": 8002,
        "blog": 8003,
        "community": 8004
    }
    
    processes = []
    
    for app, port in apps.items():
        print_colored(f"Starting {app} server on port {port}...", BLUE)
        settings = f"ram_naam_jaap.config.settings.{app}" if app != "main" else "ram_naam_jaap.config.settings"
        cmd = f"python manage.py runserver {port} --settings={settings}"
        
        try:
            process = subprocess.Popen(
                cmd, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes.append((app, port, process))
            print_colored(f"{app.capitalize()} server started on port {port}!", GREEN)
        except Exception as e:
            print_colored(f"Error starting {app} server: {e}", RED)
    
    print_colored("\nAll servers started successfully!", BOLD + GREEN)
    print_colored("Main app: http://127.0.0.1:8000", BLUE)
    print_colored("Admin app: http://127.0.0.1:8001", BLUE)
    print_colored("API: http://127.0.0.1:8002", BLUE)
    print_colored("Blog: http://127.0.0.1:8003", BLUE)
    print_colored("Community: http://127.0.0.1:8004", BLUE)
    print_colored("\nPress Ctrl+C to stop all servers.", YELLOW)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_colored("\nStopping all servers...", YELLOW)
        for app, port, process in processes:
            print_colored(f"Stopping {app} server on port {port}...", BLUE)
            process.terminate()
        print_colored("All servers stopped!", GREEN)

def create_test_data():
    """Create test data for the application"""
    print_colored("\n===== CREATING TEST DATA =====", BOLD + GREEN)
    
    # Run Django's loaddata command to load initial data
    success = run_command(
        "python manage.py loaddata initial_data", 
        "Loading initial test data"
    )
    
    if success:
        print_colored("Test data created successfully!", GREEN)
    else:
        print_colored("Failed to create test data. Please check the errors above.", RED)

def check_jinja_setup():
    """Check if Jinja2 is properly configured"""
    print_colored("\n===== CHECKING JINJA2 SETUP =====", BOLD + GREEN)
    
    # Check if Jinja2 is installed
    result = run_command(
        "pip freeze | grep Jinja2", 
        "Checking Jinja2 installation"
    )
    
    if not result:
        print_colored("Jinja2 is not installed. Installing now...", YELLOW)
        run_command("pip install Jinja2", "Installing Jinja2")
    
    # Check Jinja2 configuration in settings
    print_colored("Jinja2 setup complete!", GREEN)

def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description="Django Utility Runner for Global Applications")
    parser.add_argument("--app", choices=["main", "admin", "api", "blog", "community", "all"], 
                        default="main", help="Specify which app to run")
    parser.add_argument("--port", type=int, default=None, 
                        help="Specify the port to run the server on")
    parser.add_argument("--skip-cache", action="store_true", 
                        help="Skip cache clearing")
    parser.add_argument("--skip-static", action="store_true", 
                        help="Skip static file collection")
    parser.add_argument("--create-test-data", action="store_true", 
                        help="Create test data")
    parser.add_argument("--check-jinja", action="store_true", 
                        help="Check Jinja2 setup")
    
    args = parser.parse_args()
    
    print_colored("\n🔶 DURGA - Django Utility Runner for Global Applications 🔶", BOLD + BLUE)
    print_colored("Version 2.0.0 | Domain: ramjaap.in", BLUE)
    
    # Check if running in a virtual environment
    check_venv()
    
    # Check Jinja2 setup if requested
    if args.check_jinja:
        check_jinja_setup()
    
    # Clear cache if not skipped
    if not args.skip_cache:
        clear_cache()
    
    # Create test data if requested
    if args.create_test_data:
        create_test_data()
    
    static_success = True
    
    # Collect static files if not skipped
    if not args.skip_static:
        static_success = collect_static()
    
    if not static_success:
        print_colored("Static file collection failed. Please check the errors above.", RED)
        sys.exit(1)
    
    # Define default ports for apps
    default_ports = {
        "main": 8000,
        "admin": 8001,
        "api": 8002,
        "blog": 8003,
        "community": 8004
    }
    
    # Use user-specified port or default port for the selected app
    port = args.port if args.port else default_ports.get(args.app, 8000)
    
    # Start the server(s)
    if args.app == "all":
        start_all_servers()
    else:
        start_server(args.app, port)

if __name__ == "__main__":
    main() 