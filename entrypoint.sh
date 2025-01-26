#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata data.json

django-admin makemessages -l en
django-admin makemessages -l pl
django-admin makemessages -l es
django-admin makemessages -l fr
django-admin makemessages -l it
django-admin makemessages -l de

django-admin compilemessages

exec "$@"