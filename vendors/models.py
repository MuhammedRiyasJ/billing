from __future__ import unicode_literals
from django.db import models
from app.models import BaseModel,STATE_UT_CODE
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal
        

class Vendor(BaseModel):
    shop = models.ForeignKey('shops.Shop',limit_choices_to={"is_deleted":False})  
    vendor_id = models.PositiveIntegerField()
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=128,blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    state = models.CharField(max_length=128,choices=STATE_UT_CODE,default='32')
    balance = models.DecimalField(default=0,decimal_places=2,max_digits=15)
    gstin = models.CharField(max_length=128,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    
    
    class Meta:
        db_table = 'vendors_vendor'
        verbose_name = _('vendor')
        verbose_name_plural = _('vendors')
        ordering = ('-vendor_id',) 

    def __unicode__(self):
        return self.name
