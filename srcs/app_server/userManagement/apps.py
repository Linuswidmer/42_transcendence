from django.apps import AppConfig


class UsermanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userManagement'
    
    # def ready(self):
    #     from django.contrib.auth.models import Group

    #     # Check if the group exists, if not create it
    #     group_name = 'registered_users'
    #     if not Group.objects.filter(name=group_name).exists():
    #         Group.objects.create(name=group_name)
        
    #     group_name = 'guest_users'
    #     if not Group.objects.filter(name=group_name).exists():
    #         Group.objects.create(name=group_name)