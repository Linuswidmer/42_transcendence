TRANSCENDENCE ARCHITECTURE SETUP

# 0. General

mkdir transcendence
cd transcendence

cp DOCKER-COMPOSE.yml docker-compose.yml
cp MAKEFILE Makefile

// setup the PostgreSQL before setting up Django?

# 1.  Setting up Django in a container

virtualenv venv
source venv/bin/activate

pip install django daphne gunicorn psycopg2-binary
django-admin startproject app_server
cd app_server
cp DOCKERFILE_DJANGO Dockerfile
cp ENTRYPOINT_DJANGO.sh entrypoint.sh
chmod +x entrypoint.sh

pip freeze > requirements.txt // to write all dependencies to a text file

## adjust the Django settings
// in settings.py
import os // at the top

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(',')

## creating a new application
...

# 2. Setting up NGINX for https and wss

cd ~/transcendence

mkdir nginx
cd nginx

cp DOCKERFILE_NGINX Dockerfile
cp NGINX.CONF nginx.conf
cp -r NGINX_CERT cert



# Helpful commands
docker-compose up -d --build
docker rmi -f $(docker images -a -q)