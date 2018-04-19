#!/bin/sh
set -e 

if [ "$1" = 'manage.py' ]; then 
  echo "Starting server..."
  ./manage.py migrate
  ./manage.py collectstatic --noinput
  exec /srv/web/manage.py runserver 0.0.0.0:8000
fi
echo "Runing command..."
exec "$@"
