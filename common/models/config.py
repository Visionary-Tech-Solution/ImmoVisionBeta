from django.db import models
from common.models.base import BaseModel

class Origin(BaseModel):
    listing_url = models.URLField(null=True,blank=True)
    get_url = models.URLField(null=True,blank=True)
    name = models.CharField(max_length=200)
    

    class Meta:
        abstract = True
        
