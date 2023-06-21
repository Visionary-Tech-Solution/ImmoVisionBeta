from django.contrib import admin

from .models import ContactUs, Notification, NotificationAction

# Register your models here.
admin.site.register(Notification)
admin.site.register(NotificationAction)
admin.site.register(ContactUs)