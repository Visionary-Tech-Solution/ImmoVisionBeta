from django.contrib import admin
from order.models import BugReport, Commition, DiscountCode, Order

# Register your models here.
admin.site.register(Order)
admin.site.register(Commition)
admin.site.register(BugReport)
admin.site.register(DiscountCode)
