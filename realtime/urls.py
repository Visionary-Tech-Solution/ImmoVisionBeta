from django.urls import include, path
from realtime import views

urlpatterns = [
    path("send/", views.send_notification_now),
]