#!/usr/bin/env sh
echo "running as `id`"
sleep 5

if [ "$1" = "aragwas-worker" ]; then
    echo "Starting.... aragwas-worker"
    if [ -f /srv/web/celerybeat-schedule ]; then
        rm -f /srv/web/celerybeat-schedule
    fi
    if [ -f /srv/web/celerybeat-schedule ]; then
        rm -f /srv/web/celerybeat-schedule
    fi
    celery -A aragwas worker -B -l info
fi

if [ "$1" = "aragwas-backend" ]; then
    echo "Starting.... aragwas-backend"
    ./manage.py migrate
    ./manage.py collectstatic --no-input
    exec gunicorn aragwas.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 2 \
      --threads 4 \
      --worker-class=gthread \
      --timeout 120 \
      --log-level=info
fi