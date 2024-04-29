#!/bin/bash

. /usr/src/app/venv/bin/activate

# Function to handle SIGTERM signal
term_handler() {
    kill $GUNICORN_PID $DAPHNE_PID
    wait $GUNICORN_PID $DAPHNE_PID
    exit 0
}

# Trap the SIGTERM signal
trap 'term_handler' SIGTERM

if [ "$DATABASE" = "postgres" ]
then
        echo "Waiting for postgres..."

        while ! nc -z $SQL_HOST $SQL_PORT; do
            sleep 0.1
        done

        echo "PostgreSQL started"
fi

pip3 install --no-cache-dir -r requirements.txt

python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py shell < create_default_users.py

# Start the gunicorn server in the background
gunicorn app_server.wsgi:application --bind 0.0.0.0:8000 --log-level critical &

# Save the PID of the gunicorn server
GUNICORN_PID=$!

# Start the daphne server in the background
daphne -b 0.0.0.0 -p 8001 app_server.asgi:application -v 0 &

# Save the PID of the daphne server
DAPHNE_PID=$!

# Wait indefinitely
while true; do sleep 1; done