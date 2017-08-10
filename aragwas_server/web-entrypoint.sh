#!/bin/sh
./manage.py migrate
./manage.py collectstatic
./manage.py runserver 0.0.0.0:8000
