#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Add the ram_naam_jaap directory to the Python path
    project_path = os.path.dirname(os.path.abspath(__file__))
    ram_naam_jaap_path = os.path.join(project_path, 'ram_naam_jaap')
    sys.path.insert(0, project_path)
    sys.path.insert(0, ram_naam_jaap_path)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
