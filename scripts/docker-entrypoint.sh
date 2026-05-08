#!/usr/bin/env sh
set -e

cd /app/ram_naam_jaap

if [ "$1" = "web" ]; then
  mkdir -p /app/ram_naam_jaap/logs
  python ../manage.py migrate --noinput
  python ../manage.py collectstatic --noinput
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
fi

exec "$@"
