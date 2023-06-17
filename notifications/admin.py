from django.contrib import admin

from .models import Notification, NotificationAction

# Register your models here.
admin.site.register(Notification)
admin.site.register(NotificationAction)