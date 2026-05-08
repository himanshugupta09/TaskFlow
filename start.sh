#!/bin/bash
set -e

echo "Starting TaskFlow deployment..."
cd /app

echo "Running migrations..."
python taskflow/manage.py migrate

echo "Collecting static files..."
python taskflow/manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 3 \
  --log-file - \
  taskflow.wsgi:application
