#!/bin/bash 

echo "Making migrations and migrating the database. "
python manage.py makemigrations --noinput 
python manage.py migrate --noinput 
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput
echo starting gunicorn
gunicorn -c gunicorn_conf.py conquest_back.wsgi:application --bind 0.0.0.0:9000
