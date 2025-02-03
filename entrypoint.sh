#!/bin/sh

python manage.py makemigrations
python manage.py migrate
# Uncomment on when it was your first time firing up the app
#python manage.py loaddata data.json

# django-admin makemessages -l en
# django-admin makemessages -l pl
# django-admin makemessages -l es
# django-admin makemessages -l fr
# django-admin makemessages -l it
# django-admin makemessages -l de

# django-admin compilemessages
# python manage.py collectstatic
exec "$@"