from __future__ import unicode_literals
from django.db import models
from app.models import BaseModel
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class Purchase(BaseModel):
    shop = models.ForeignKey('shops.Shop',limit_choices_to={"is_deleted":False})
    purchase_id = models.CharField(max_length=128)
    date = models.DateTimeField(default=timezone.now)
    vendor = models.ForeignKey('vendors.Vendor',limit_choices_to={"is_deleted":False},blank=True,null=True)
    purchase_date = models.DateTimeField(blank=True,null=True)
    invoice_no = models.CharField(max_length=120,blank=True,null=True)
    other_charges = models.DecimalField(default=0.0,decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    final_total = models.DecimalField(default=0.0,decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    paid = models.DecimalField(default=0.0,decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    balance = models.DecimalField(default=0.0,decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    purchase_type = models.CharField(max_length=128,choices=(('intra_state','Intra State'),('inter_state','Inter State')),default='intra_state')
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'purchase'
        verbose_name = _('purchase')
        verbose_name_plural = _('purchases')
        ordering = ('-date',)
    
    class Admin:
        list_display = ('-date',)

    def __unicode__(self):
        return str(self.purchase_id)


class PurchaseProduct(models.Model):
    purchase = models.ForeignKey('purchases.Purchase',limit_choices_to={"is_deleted":False})
    product = models.ForeignKey('products.Product',limit_choices_to={"is_deleted":False})
    unit_cost = models.DecimalField(decimal_places=2, max_digits=15,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    input_gst = models.DecimalField(decimal_places=2, max_digits=15,blank=True,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    quantity = models.PositiveIntegerField()
    offer = models.DecimalField(decimal_places=2, max_digits=15,blank=True,null=True,validators=[MinValueValidator(Decimal('0.00'))])
    tax_amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15, validators=[MinValueValidator(Decimal('0.00'))])
    amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15,null=True, validators=[MinValueValidator(Decimal('0.00'))])
    total_amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15, validators=[MinValueValidator(Decimal('0.00'))])
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'purchase_product'
        verbose_name = _('purchase product')
        verbose_name_plural = _('purchase products')
        ordering = ('purchase','id',)
    
    class Admin:
        list_display = ('purchase',)

    def __unicode__(self):
        return str(self.purchase)      