from django.db import models

from common.models.base import BaseModel


class SellHouseAddress(BaseModel):
    line1 = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    line2 = models.CharField(max_length=100, null=True, blank=True)
    postalCode = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.line1}, {self.postalCode}, {self.city}"


# class Address(BaseModel):
#     line1 = models.CharField(max_length=100, null=True, blank=True)
#     state = models.CharField(max_length=100, null=True, blank=True)
#     line2 = models.CharField(max_length=100, null=True, blank=True)
#     postalCode = models.CharField(max_length=100, null=True, blank=True)
#     city = models.CharField(max_length=100, null=True, blank=True)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

#     def __str__(self):
#         return f"{self.line1}, {self.postalCode}, {self.city}"
        
