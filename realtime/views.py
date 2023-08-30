from django.shortcuts import render
from django.http import HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Trigger a notification for a specific user
def send_notification_to_user(user_email, notification_text):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_email}",
        {
            'type': 'send_notification',
            'notification': {'text': notification_text}
        }
    )



def send_notification_now(request):

    print(request.user)
    send_notification_to_user(request.user.email,"Hello world")

    return HttpResponse("Created sended")