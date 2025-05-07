#!/bin/bash

# ANSI color codes for terminal output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Function to ensure the virtual environment is activated
ensure_venv() {
    if [[ -z "${VIRTUAL_ENV}" ]]; then
        print_message "📦 Activating virtual environment..." "${CYAN}"
        source venv/bin/activate
    fi
}

# Function to run a command
run_command() {
    print_message "🔄 $1..." "${CYAN}"
    eval "$2"
    local status=$?
    if [ $status -eq 0 ]; then
        print_message "✅ $1 completed successfully" "${GREEN}"
    else
        print_message "❌ $1 failed with status $status" "${RED}"
        exit $status
    fi
}

# Display help message
show_help() {
    print_message "Ram Naam Jaap Project Helper" "${GREEN}"
    print_message "----------------------------" "${GREEN}"
    print_message "Usage: ./ramjaap.sh [command]" "${CYAN}"
    print_message "\nAvailable commands:" "${YELLOW}"
    print_message "  start      - Clear cache, collect static files, and start the development server"
    print_message "  test       - Run tests for the project"
    print_message "  makemigr   - Create migrations for model changes"
    print_message "  migrate    - Apply database migrations"
    print_message "  collectstatic - Collect static files"
    print_message "  clearcache - Clear Django and Python cache files"
    print_message "  shell      - Start Django shell"
    print_message "  createsuperuser - Create a superuser"
    print_message "  check      - Run Django system checks"
    print_message "  help       - Show this help message"
}

# Ensure we're in the project root directory
ensure_venv

# Process command line arguments
case "$1" in
    start)
        print_message "🚀 Starting development server with clean cache and fresh static files..." "${GREEN}"
        run_command "Running durga.py" "python durga.py"
        ;;
    test)
        print_message "🧪 Running tests..." "${GREEN}"
        run_command "Running tests" "python manage.py test"
        ;;
    makemigr)
        print_message "📝 Making migrations..." "${GREEN}"
        run_command "Making migrations" "python manage.py makemigrations"
        ;;
    migrate)
        print_message "🔄 Applying migrations..." "${GREEN}"
        run_command "Applying migrations" "python manage.py migrate"
        ;;
    collectstatic)
        print_message "📦 Collecting static files..." "${GREEN}"
        run_command "Collecting static files" "python manage.py collectstatic --noinput"
        ;;
    clearcache)
        print_message "🧹 Clearing cache..." "${GREEN}"
        run_command "Clearing cache" "python durga.py clearcache"
        ;;
    shell)
        print_message "🐚 Starting Django shell..." "${GREEN}"
        run_command "Starting shell" "python manage.py shell"
        ;;
    createsuperuser)
        print_message "👤 Creating superuser..." "${GREEN}"
        run_command "Creating superuser" "python manage.py createsuperuser"
        ;;
    check)
        print_message "🔍 Running system checks..." "${GREEN}"
        run_command "Running checks" "python manage.py check"
        ;;
    help|*)
        show_help
        ;;
esac

print_message "\n✨ Command completed! ✨" "${GREEN}"
exit 0 