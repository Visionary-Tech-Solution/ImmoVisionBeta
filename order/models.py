import uuid

from account.models import BrokerProfile, FreelancerProfile, Profile
from common.models.address import SellHouseAddress
from common.models.base import BaseModel
from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
User = get_user_model()


class Commition(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    commition = models.CharField(max_length=100)

class Order(BaseModel):
    ASSISTANT_TYPE_CHOICES = [
        ('male', 'Male'),
        ( 'female', 'Female'),
    ]
    LANGUAGE_TYPE_CHOICES = [
        ('english', 'English'),
        ( 'french', 'French'),
    ]
    STATUS_TYPE = [
        ('pending',"PENDING"),
        ('assigned',"ASSIGNED"),
        ('in_progress',"In Progress"),
        ('completed', "Completed"),
        ('demo', "Demo"),
        ('in_review', "In Review"),
        ('canceled',"Canceled")
    ]
    ORDER_TYPE_CHOICES = [
        ('teaser', "Teaser"),
        ('full_house', "Full House"),
    ]
    order_sender = models.ForeignKey(BrokerProfile, on_delete = models.CASCADE)
    zpid = models.CharField(max_length=150, null=True, blank=True)
    url = models.CharField(max_length=150)
    client_name = models.CharField(max_length=150)
    assistant_type = models.CharField(max_length=70, choices=ASSISTANT_TYPE_CHOICES)
    video_language = models.CharField(max_length=70, choices=LANGUAGE_TYPE_CHOICES)
    address = models.CharField(max_length=255, null=True, blank=True)
    amount = models.CharField(max_length=100)
    status = models.CharField(max_length=80, choices=STATUS_TYPE,  null=False, blank=False)
    order_receiver = models.ForeignKey(FreelancerProfile, on_delete=models.SET_NULL, null=True, blank=True)
    order_assign_time = models.TimeField(null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=100)
    apply_subtitle = models.BooleanField(default=True)
    demo_video = models.BooleanField(default=False)
    property_address = models.ForeignKey(SellHouseAddress, on_delete=models.SET_NULL, null=True, blank=True)
    property_photo_url = models.CharField(max_length=300, blank=True, null=True)
    property_details = models.TextField(null=True, blank=True)
    order_type = models.CharField(max_length=80, choices=ORDER_TYPE_CHOICES, null=True, blank=True)
    order_commission = models.ForeignKey(Commition, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.FileField(upload_to='order/invoices/', null=True, blank=True)
    delivery_time = models.CharField(max_length=40, null=True, blank=True)
    order_video = models.CharField(max_length=145, null=True, blank=True)
    rating = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    _id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        # return f"{self.order_receiver.profile.username}"
        return f"{self._id}"

class Amount(BaseModel):
    _id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return f"{self._id}"

class MaxOrder(BaseModel):
    _id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    max_order = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return f"{self._id}"

class DiscountCode(BaseModel):
    _id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, unique=True)
    valid_date = models.DateField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.code}"


class BugReport(BaseModel):
    bug_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    bug_details = models.CharField(max_length=600, null=False, blank=False)
    is_solve = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bug_id}"


