from django.db import models


class BaseModel(models.Model):
    modified_at = models.DateTimeField(auto_now=True, verbose_name='Modified at')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    deleted_at = models.DateTimeField(verbose_name='Deleted at', null=True, blank=True)

    class Meta:
        abstract = True
        
