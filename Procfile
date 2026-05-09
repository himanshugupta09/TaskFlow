web: cd taskflow && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60 --access-logfile - taskflow.wsgi
