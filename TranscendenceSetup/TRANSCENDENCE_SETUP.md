TRANSCENDENCE ARCHITECTURE SETUP

# 0. General

mkdir transcendence
cd transcendence

cp DOCKER-COMPOSE.yml docker-compose.yml
cp ENV.DEV env.dev
cp MAKEFILE Makefile


# 1. Setup postgre SQL

// update the settings.py Databases environment variables
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

# 2.  Setting up Django in a container

virtualenv venv
source venv/bin/activate

pip install django daphne gunicorn psycopg2-binary channels
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

## creating a new application and serving a static file

source venv/bin/activate
django-admin startapp pong

// create a file called urls.py in pong/
cd pong
touch urls.py

//urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

// adjust the views.py
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'pong/index.html')


// create the folder for static files
mkdir templates
cd templates
mkdir pong
touch pong/index.html


// adjust the appserver/settings.py
~/app_server

//add the "pong" to INSTALLED_APPS
INSTALLED_APPS = [
    [...],
    'pong',
]

//adjust the appserver/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('pong.urls')),
    path('admin/', admin.site.urls),
]

## serve websocket connections

// add 'channels to the INSTALLED APPS'
 INSTALLED_APPS = [
    'channels',
]

// IMPORTANT!!!
// setup a routing.py in app_server to handle incoming ws connections
// setup the app_server/asgi.py which is used to launch daphne for incoming ws connections
// the appp_server/asgi.py relies on the pong/routing.py for url pattern matching



# 3. Setting up NGINX for https and wss

cd ~/transcendence

mkdir nginx
cd nginx

cp DOCKERFILE_NGINX Dockerfile
cp NGINX.CONF nginx.conf
cp -r NGINX_CERT cert


# Helpful commands
docker-compose up -d --build
docker rmi -f $(docker images -a -q)

# Development server

export DJANGO_SECRET_KEY="your_secret_key_here"
export DJANGO_DEBUG="1"  
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

python3 manage.py runserver 127.0.0.1:8443

