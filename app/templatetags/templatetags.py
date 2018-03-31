from django import template
from purchases.models import PurchaseProduct
from sales.models import SaleProduct
from django.db.models import Sum
from decimal import Decimal


register = template.Library()

@register.filter
def value(value,arg):
	return value * arg

@register.filter
def grossvalue(value,rate):
	rate = rate if rate else Decimal('0.0')
	gross = value + value * rate/100
	return gross

@register.filter
def purchase_total(value,arg):
	if arg:
		total_amount =PurchaseProduct.objects.filter(purchase=value,is_deleted=False,product__untaxed=False).aggregate(Sum('total_amount'))['total_amount__sum']
	else:
		total_amount = PurchaseProduct.objects.filter(purchase=value,is_deleted=False).aggregate(Sum('total_amount'))['total_amount__sum']

	total_amount=total_amount if total_amount else "0.00"

	return total_amount


@register.filter
def purchase_products_exists(value,arg):

	dispaly_purchase=True
	if arg and not PurchaseProduct.objects.filter(purchase=value,is_deleted=False,product__untaxed=False).exists():
		dispaly_purchase = False

	return dispaly_purchase

@register.filter
def sale_total(value,arg):
	if arg:
		total_amount =SaleProduct.objects.filter(sale=value,is_deleted=False,product__untaxed=False).aggregate(Sum('total_amount'))['total_amount__sum']
	else:
		total_amount = SaleProduct.objects.filter(sale=value,is_deleted=False).aggregate(Sum('total_amount'))['total_amount__sum']

	total_amount=total_amount if total_amount else "0.00"

	return total_amount


@register.filter
def sale_products_exists(value,arg):

	dispaly_sale=True
	if arg and not SaleProduct.objects.filter(sale=value,is_deleted=False,product__untaxed=False).exists():
		dispaly_sale = False

	return dispaly_sale



@register.filter
def fraction(value,divisible):
	return Decimal(value)/Decimal(divisible)


