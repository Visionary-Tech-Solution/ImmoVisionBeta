from django.contrib import admin

from order.models import (Amount, BugReport, Commition, DiscountCode, MaxOrder,
                          Order)

# Register your models here.
admin.site.register(Order)
admin.site.register(MaxOrder)
admin.site.register(Commition)
admin.site.register(BugReport)
admin.site.register(DiscountCode)
admin.site.register(Amount)
