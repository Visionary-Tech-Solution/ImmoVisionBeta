from account.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers


class EmailSerializer(serializers.Serializer):

    email = serializers.EmailField()

    class Meta:
        fields = ("email",)



class ResetPasswordSerializer(serializers.Serializer):
    password_reset_token = serializers.CharField()
    new_password = serializers.CharField()
    class Meta:
        fields = ("password_reset_token", "new_password")



