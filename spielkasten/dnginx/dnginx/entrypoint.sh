#!/bin/ash

echo "Applying migrations"
python manage.py migrate

exec "$@"