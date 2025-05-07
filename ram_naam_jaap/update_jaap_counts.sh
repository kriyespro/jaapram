#!/bin/bash

# Script to update jaap counts for dummy devotees
# To be run as a cron job

# Go to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the management command to update jaap counts
python manage.py generate_dummy_data update

# Log the execution time
echo "Jaap counts updated on $(date)" >> jaap_update.log

# Exit
exit 0 