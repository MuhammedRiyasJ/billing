from django.db import models
from app.models import BaseModel
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

class Expense(BaseModel):
    shop = models.ForeignKey('shops.Shop',limit_choices_to={"is_deleted":False})
    date = models.DateTimeField()
    amount = models.DecimalField(default=0.0,decimal_places=2, max_digits=15, validators=[MinValueValidator(Decimal('0.00'))])
    description = models.TextField(max_length=256,null=True,blank=True)

    is_deleted = models.BooleanField(default=False)
     
    class Meta:
        db_table = 'expense'
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        ordering = ('-date',)        
  
    def __unicode__(self):
        return self