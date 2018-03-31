from django.db import models
from app.models import BaseModel
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _


class Product(BaseModel):
    shop = models.ForeignKey('shops.Shop',limit_choices_to={"is_deleted":False})
    product_id = models.PositiveIntegerField()
    hsn_code = models.CharField(max_length=128,blank=True,null=True)
    name = models.CharField(max_length=128)
    unit_price = models.DecimalField(default=0,decimal_places=2, max_digits=15,validators=[MinValueValidator(Decimal('0.00'))])
    input_gst = models.DecimalField(default=0,decimal_places=2, max_digits=15,validators=[MinValueValidator(Decimal('0.00'))])
    output_gst = models.DecimalField(default=0,decimal_places=2, max_digits=15,validators=[MinValueValidator(Decimal('0.00'))])
    stock = models.PositiveIntegerField(default=0)
    untaxed = models.BooleanField(default=False,blank=True)

    is_deleted = models.BooleanField(default=False)
     
    class Meta:
        db_table = 'product'
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ('product_id',)      
  
    def __unicode__(self):
        return self.name