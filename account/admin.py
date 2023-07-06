from account.models import (BrokerProfile, BrokersFileCSV, FreelancerProfile,
                            IpAddress, PaymentMethod, Profile)
from django.contrib import admin

# Register your models here.
admin.site.register(Profile)
admin.site.register(BrokerProfile)
admin.site.register(PaymentMethod)
admin.site.register(FreelancerProfile)
admin.site.register(BrokersFileCSV)
admin.site.register(IpAddress)
