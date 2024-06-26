from django.contrib import admin

from account.models import (BrokerProfile, BrokersFileCSV,
                            FreelancerPaymentMethod, FreelancerProfile,
                            FreelancerWithdraw, IpAddress, PaymentMethod,
                            Profile, ProfilePicture)

# Register your models here.
admin.site.register(Profile)
admin.site.register(ProfilePicture)
admin.site.register(BrokerProfile)
admin.site.register(PaymentMethod)
admin.site.register(FreelancerProfile)
admin.site.register(BrokersFileCSV)
admin.site.register(IpAddress)
admin.site.register(FreelancerPaymentMethod)
admin.site.register(FreelancerWithdraw)
