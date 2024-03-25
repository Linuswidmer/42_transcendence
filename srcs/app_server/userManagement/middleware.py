# from django.utils import timezone
# from .models import Profile

# class UpdateUserActivityMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)

#         if request.user.is_authenticated:
#             request.user.profile.last_activity = timezone.now()
#             request.user.profile.save()
#         return response
    
#add UpdateUserActivityMiddleware in settings.py