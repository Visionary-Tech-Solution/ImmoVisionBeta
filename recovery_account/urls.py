from django.contrib import admin
from django.urls import path
from .views import (
    PasswordReset,
    ResetPasswordSendTokenApi
)

urlpatterns = [
    path('reset-password/', PasswordReset.as_view(), name="reset-password"),
    path('reset-password-send-token/',ResetPasswordSendTokenApi.as_view(), name="reset-password-send-token"),
]
