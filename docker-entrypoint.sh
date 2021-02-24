#!/bin/sh

./python_venv/bin/python3 manage.py migrate                  # Apply database migrations
./python_venv/bin/python3 manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
echo Starting Gunicorn.
exec ./python_venv/bin/gunicorn -c hdt_monitor/settings/gunicorn_config.py hdt_monitor.wsgi:application
