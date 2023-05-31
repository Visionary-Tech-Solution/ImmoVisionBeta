from .models import Notification

def notification_tem(user, title, desc, notification_type):
    Notification.objects.create(
        user = user,
        title = title,
        desc = desc,
        notification_type = notification_type
    )