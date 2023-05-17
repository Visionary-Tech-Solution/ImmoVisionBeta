from account.models import BrokerProfile, FreelancerProfile, Profile
from django.contrib import admin

# Register your models here.
admin.site.register(Profile)
admin.site.register(BrokerProfile)
admin.site.register(FreelancerProfile)
