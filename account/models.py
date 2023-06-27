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
    stripe_customer_id = models.CharField(max_length=100, default="", null=True, blank=True)
    payment_method_id = models.CharField(max_length=100, default="", null=True, blank=True)
    payment_type = models.CharField(max_length=100, null=True, blank=True)
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
    language = models.CharField(max_length=255, null=True, blank=True, default="English")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='broker_profile')
    real_estate_agency = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    active_orders = models.IntegerField(default=0,  null=True, blank=True)
    is_demo = models.BooleanField(default=False)
    total_orders = models.IntegerField(default=0,  null=True, blank=True)

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
        ( 'unsuspended', 'Unsuspended'),
        ('not_available', 'Not available'),
        ('terminated', 'Terminated')
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='freelancer_profile')
    active_work = models.IntegerField(default=0, null=True, blank=True)
    total_work = models.IntegerField(default=0, null=True, blank=True)
    total_revenue = models.IntegerField(default=0,  null=True, blank=True)
    pending_earn = models.IntegerField(default=0,  null=True, blank=True)
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
    

class PaymentMethod(BaseModel):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stripe_payment_method_id = models.CharField(max_length=100)
    last4 = models.CharField(max_length=4)
    exp_month = models.PositiveIntegerField()
    exp_year = models.PositiveIntegerField()