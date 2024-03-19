from django.contrib import admin
from .models import Tournaments, Games, UserGameStats
admin.site.register(Tournaments)
admin.site.register(Games)
admin.site.register(UserGameStats)
# Register your models here.
