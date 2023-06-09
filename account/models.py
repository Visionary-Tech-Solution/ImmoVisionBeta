import uuid

from common.models.base import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='immovision/images/profile_pics/', blank=True, default='default_file/sample.png')
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    username=models.CharField(max_length=80,unique=True)
    email=models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.username}"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance ,  username = instance.username, email = instance.email)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


class BrokerProfile(BaseModel):
    zuid = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='broker_profile')
    real_estate_agency = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    active_orders = models.IntegerField(default=0,  null=True, blank=True)

    def __str__(self):
        return f"{self.profile.username}"
    
    @receiver(post_save, sender=Profile)
    def create_profile(sender, instance, created, **kwargs):
        if instance.user.type == 'BROKER':
            if created:
                BrokerProfile.objects.create(profile=instance)

    @receiver(post_save, sender=Profile)
    def save_profile(sender, instance, **kwargs):
        if instance.user.type == 'BROKER':
            instance.broker_profile.get().save()
    

class FreelancerProfile(BaseModel):
    STATUS_TYPE_CHOICES = [
        ('active', 'Active'),
        ( 'suspended', 'Suspended'),
        ('not_available', 'Not available'),
        ('terminated', 'Terminated')
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='freelancer_profile')
    active_work = models.IntegerField(default=0, null=True, blank=True)
    total_work = models.IntegerField(default=0, null=True, blank=True)
    total_revenue = models.CharField(max_length=30, default='0.00')
    pending_earn = models.CharField(max_length=30, default='0.00')
    bug_rate = models.IntegerField(default=0, null=True, blank=True)
    late_task = models.IntegerField(default=0,null=True, blank=True)
    status_type = models.CharField(max_length=60, choices=STATUS_TYPE_CHOICES, default="active")
    freelancer_status = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.profile.username} -> Freelancer"
    
    @receiver(post_save, sender=Profile)
    def create_profile(sender, instance, created, **kwargs):
        if instance.user.type == 'FREELANCER':
            if created:
                FreelancerProfile.objects.create(profile=instance)

    @receiver(post_save, sender=Profile)
    def save_profile(sender, instance, **kwargs):
        if instance.user.type == 'FREELANCER':
            instance.freelancer_profile.get().save()


# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notification')
#     title = models.CharField(max_length=250, null=True, blank=True)


class BrokersFileCSV(BaseModel):
    file = models.FileField(upload_to="broker_dataset_files")

    def __str__(self):
        return f"{self.file}, {self.id}"