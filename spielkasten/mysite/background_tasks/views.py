# your_app/views.py
from django.shortcuts import render
from .tasks import background_task
from django.http import HttpResponse


def index(request):
    # Trigger the background task
    result = background_task.delay(10, 20)

    try:
        result_value = result.get(timeout=10)  # Wait up to 10 seconds
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
    return HttpResponse(f"The result is {result_value}")

    # return render(request, 'background_tasks/index.html')