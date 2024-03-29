# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# create a Celery instance and configure it using the settings from Django
celery_app = Celery('mysite')

# Load task modules from all registered Django app configs.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
celery_app.autodiscover_tasks()

app = Celery('background_tasks',
             broker='redis://localhost:6379/0',  # Redis as message broker
             backend='redis://localhost:6379/0',  # Redis as result backend
             include=['background_tasks.tasks']
             )

app.conf.update(
        CELERY_TASK_SERIALIZER = 'json',
        CELERY_RESULT_SERIALIZER = 'json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE = 'Europe/Oslo',
        CELERY_ENABLE_UTC = True
                )