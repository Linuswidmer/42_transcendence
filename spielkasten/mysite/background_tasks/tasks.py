from celery import shared_task

@shared_task
def background_task(arg1, arg2):
    # Your background task logic goes here
    result = arg1 + arg2
    return result