from products.models import Product
from django.shortcuts import get_object_or_404


def remove_previous_product_stock(pre_product,pre_stock):
    
    #getting previous product_stock
    stocks = Product.objects.filter(name=pre_product)
    
    #updating previous changes in product
    if stocks.exists():
        stock_obj = get_object_or_404(stocks)
        quantity = stock_obj.stock - pre_stock
        stocks.update(stock=quantity)
    