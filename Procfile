release: python manage.py migrate --noinput && python manage.py add_fotomultas_resource
web: gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2
