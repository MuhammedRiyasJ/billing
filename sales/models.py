from __future__ import unicode_literals
from django.db import models
from app.models import BaseModel
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class Sale(BaseModel):
    shop = models.ForeignKey('shops.Shop',limit_choices_to={"is_deleted":False})
    sale_id = models.CharField(max_length=128)
    date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey('customers.Customer',limit_choices_to={"is_deleted":False},blank=True,null=True)
    sale_type = models.CharField(max_length=128,choices=(('intra_state','Intra State'),('inter_state','Inter State')),default='intra_state')
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sale'
        verbose_name = _('sale')
        verbose_name_plural = _('sales')
        ordering = ('-date_added',) 
    
    class Admin:
        list_display = ('date',)

    def __unicode__(self):
        return str(self.sale_id)


class SaleProduct(models.Model):
    sale = models.ForeignKey('sales.Sale',limit_choices_to={"is_deleted":False})
    product = models.ForeignKey('products.Product',limit_choices_to={"is_deleted":False})
    unit_price = models.DecimalField(decimal_places=2, max_digits=15,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    output_gst = models.DecimalField(decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    quantity = models.PositiveIntegerField()
    offer = models.DecimalField(decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    tax_amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15, validators=[MinValueValidator(Decimal('0.00'))])
    amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    total_amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15, validators=[MinValueValidator(Decimal('0.00'))])
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sale_product'
        verbose_name = _('sale product')
        verbose_name_plural = _('sale products')
        ordering = ('sale','id',)

    class Admin:
        list_display = ('product',)

    def __unicode__(self):
        return product