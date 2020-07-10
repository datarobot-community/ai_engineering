#!/usr/bin/env bash
# start-server.sh
#(cd drdecisions; python manage.py runserver)

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd drdecisions; python manage.py createsuperuser --no-input)
fi
(cd drdecisions; gunicorn drdecisions.wsgi --user www-data --bind 127.0.0.1:8001 --workers 1) &
nginx -g "daemon off;"
