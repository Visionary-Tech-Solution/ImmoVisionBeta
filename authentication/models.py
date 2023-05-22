from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError(_('Please enter an email address'))

        email=self.normalize_email(email)

        new_user=self.model(email=email,**extra_fields)

        new_user.set_password(password)

        new_user.save()

        return new_user


    def create_superuser(self,email,password,**extra_fields):

        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))


        return self.create_user(email,password,**extra_fields)


class User(AbstractUser):
    USER_TYPE = [
        ("UNSPECIFIED", "Unspecified"),
        ("BROKER", "Broker"),
        ("FREELANCER", "Freelancer"),
        ("ADMIN", "Admin"),
    ]

    first_name=models.CharField(_('First Name'), max_length=50, null=True, blank=True)
    last_name=models.CharField(_('Last Name'), max_length=50, null=True, blank=True)
    username=models.CharField(_('Username'), max_length=80,unique=True)
    email=models.CharField(_('Email'), max_length=100,unique=True)
    type = models.CharField(max_length=80, choices=USER_TYPE, blank=False, null=False,
                            default="UNSPECIFIED")
    date_joined=models.DateTimeField(_('Date'),auto_now_add=True)

    REQUIRED_FIELDS=['email']
    USERNAME_FIELD='username'

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"