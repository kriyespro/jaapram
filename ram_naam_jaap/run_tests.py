#!/Users/kumarsunilverma/Desktop/sd-dj-test-1/ram_naam_jaap/ram_naam_jaap/venv/bin/python
"""
Comprehensive test runner for Ram Naam Jaap application
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
import django
django.setup()

from django.core.management import call_command

# Path to python executable in venv
PYTHON_PATH = os.path.join('ram_naam_jaap', 'venv', 'bin', 'python')

def run_unit_tests(apps=None, verbosity=1, failfast=False):
    """Run unit tests for specified apps or all apps"""
    print("\n📋 Running unit tests...\n")
    
    args = ['test']
    if apps:
        args.extend(apps.split(','))
    
    kwargs = {
        'verbosity': verbosity,
        'failfast': failfast,
    }
    
    return call_command(*args, **kwargs)


def run_coverage(apps=None):
    """Run tests with coverage report"""
    print("\n📊 Running tests with coverage...\n")
    
    cmd = [PYTHON_PATH, '-m', 'coverage', 'run', '--source=.', 'manage.py', 'test']
    if apps:
        cmd.extend(apps.split(','))
    
    try:
        subprocess.run(cmd, check=True)
        subprocess.run([PYTHON_PATH, '-m', 'coverage', 'report'], check=True)
        subprocess.run([PYTHON_PATH, '-m', 'coverage', 'html'], check=True)
        print("\n✅ Coverage report generated in htmlcov/index.html")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running coverage: {e}")
        return False
    
    return True


def run_flake8():
    """Run flake8 code quality checks"""
    print("\n🔍 Running code quality checks with flake8...\n")
    
    try:
        # Exclude migrations, venv, and other non-essential files
        cmd = [
            PYTHON_PATH, '-m', 'flake8', 
            '--exclude=migrations,venv,__pycache__',
            '--max-line-length=100'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ No code quality issues found!")
            return True
        else:
            print("❌ Code quality issues found:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error running flake8: {e}")
        return False


def run_system_checks():
    """Run Django system checks"""
    print("\n🔧 Running Django system checks...\n")
    call_command('check', '--deploy')
    return True


def run_all_tests(apps=None, verbosity=1, failfast=False):
    """Run all test types"""
    results = {}
    
    # Run unit tests
    try:
        run_unit_tests(apps, verbosity, failfast)
        results['unit_tests'] = True
    except Exception:
        results['unit_tests'] = False
    
    # Run system checks
    try:
        run_system_checks()
        results['system_checks'] = True
    except Exception:
        results['system_checks'] = False
    
    # Run coverage if available
    try:
        import coverage
        results['coverage'] = run_coverage(apps)
    except ImportError:
        print("⚠️ Coverage not available. Install it with: pip install coverage")
        results['coverage'] = None
    
    # Run flake8 if available
    try:
        import flake8
        results['flake8'] = run_flake8()
    except ImportError:
        print("⚠️ Flake8 not available. Install it with: pip install flake8")
        results['flake8'] = None
    
    # Display summary
    print("\n📝 Test Summary:")
    for test_type, result in results.items():
        if result is True:
            print(f"✅ {test_type}: PASSED")
        elif result is False:
            print(f"❌ {test_type}: FAILED")
        else:
            print(f"⚠️ {test_type}: SKIPPED")
    
    # Return overall success status
    return all(result for result in results.values() if result is not None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run tests for Ram Naam Jaap application')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--flake8', action='store_true', help='Run flake8 code quality checks')
    parser.add_argument('--system-check', action='store_true', help='Run Django system checks')
    parser.add_argument('--all', action='store_true', help='Run all test types')
    parser.add_argument('--apps', type=str, help='Comma-separated list of apps to test')
    parser.add_argument('--verbosity', type=int, default=1, help='Verbosity level (0-3)')
    parser.add_argument('--failfast', action='store_true', help='Stop tests on first failure')
    
    args = parser.parse_args()
    
    # Default to running unit tests if no test type specified
    if not any([args.unit, args.coverage, args.flake8, args.system_check, args.all]):
        args.unit = True
    
    success = True
    
    if args.all:
        success = run_all_tests(args.apps, args.verbosity, args.failfast)
    else:
        if args.unit:
            try:
                run_unit_tests(args.apps, args.verbosity, args.failfast)
            except Exception:
                success = False
        
        if args.coverage:
            if not run_coverage(args.apps):
                success = False
        
        if args.flake8:
            if not run_flake8():
                success = False
        
        if args.system_check:
            try:
                run_system_checks()
            except Exception:
                success = False
    
    if not success:
        sys.exit(1) 