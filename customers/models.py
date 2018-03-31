from django.db import models
from app.models import BaseModel,STATE_UT_CODE
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _

class Customer(BaseModel):
    shop = models.ForeignKey('shops.Shop',limit_choices_to={"is_deleted":False})
    customer_id = models.PositiveIntegerField()
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=128,blank=True,null=True)
    email = models.EmailField(max_length=70,blank=True,null=True)
    details = models.TextField(max_length=256,null=True,blank=True)
    gstin = models.CharField(max_length=128,blank=True,null=True)
    state = models.CharField(max_length=128,choices=STATE_UT_CODE,default='32')
    cst = models.CharField(max_length=128,blank=True,null=True)
    balance = models.DecimalField(default=0,decimal_places=2,max_digits=15)

    is_deleted = models.BooleanField(default=False)
     
    class Meta:
        db_table = 'customer'
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        ordering = ('-customer_id',)        
  
    def __unicode__(self):
        return self.name