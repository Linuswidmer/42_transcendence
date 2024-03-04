import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcelery.settings')

app = Celery('dcelery')
app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task
def add_numbers():
    return
# celery will look in all installed apps for a file named tasks.py and load any tasks defined there.
app.autodiscover_tasks()