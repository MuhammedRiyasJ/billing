from __future__ import unicode_literals
from django.db import models
from app.models import BaseModel
from django.utils.translation import ugettext_lazy as _
        


class Shop(BaseModel):
    shop_id = models.PositiveIntegerField()
    name = models.CharField(max_length=128,unique=True)
    location = models.CharField(max_length=128)
    contact_no = models.CharField(max_length=128)
    gstin = models.CharField(max_length=128,blank=True,null=True)
    cst = models.CharField(max_length=128,blank=True,null=True)
    
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'shops_shop'
        verbose_name = _('shop')
        verbose_name_plural = _('shops')
        ordering = ('shop_id',) 

    def __unicode__(self):
        return self.name