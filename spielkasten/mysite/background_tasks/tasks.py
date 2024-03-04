# from celery import shared_task

# @shared_task
# def background_task(arg1, arg2):
#     print('background_task activated!')
#     # result = arg1 + arg2
#     # return result

from celery import Celery

app = Celery('tasks', broker='redis://guest@localhost//')

@app.task
def add(x, y):
    return x + y