from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
from app.functions import get_current_shop
from app.models import Notification
from sales.models import Sale,SaleProduct
from products.models import Product
from customers.models import Customer
from vendors.models import Vendor
from purchases.models import Purchase,PurchaseProduct
from expense.models import Expense
from users.models import Profile
from django.db.models import Sum
import datetime
from decimal import Decimal
from django.db.models import Q

@login_required
def dashboard(request):

    if request.user.is_superuser:

        total_sale = Decimal('0.00')
        total_purchase = Decimal('0.00')
        paid_purchase = Decimal('0.00')
        balance_purchase = Decimal('0.00')
        total_expense = Decimal('0.00')

    else:
        current_shop = get_current_shop(request)
        user_profile = Profile.objects.get(user=request.user)
        start_date = datetime.datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
        end_date = datetime.datetime.now()
        
        #dashboard for sale details
        sale_list = Sale.objects.filter(is_deleted=False , shop=current_shop,date__range=[start_date,end_date])

        if user_profile.tax_only:
            sale_product_list = SaleProduct.objects.filter(sale__in=sale_list,is_deleted=False,product__untaxed=False)
        else:
            sale_product_list = SaleProduct.objects.filter(sale__in=sale_list,is_deleted=False)

        total_sale = sale_product_list.aggregate(Sum('total_amount'))['total_amount__sum']
        total_sale = total_sale if total_sale else Decimal('0.00')

        #dashboard for purchase details
        purchase_list = Purchase.objects.filter(is_deleted=False , shop=current_shop,date__range=[start_date,end_date])

        if user_profile.tax_only:
            purchase_product_list = PurchaseProduct.objects.filter(is_deleted=False, purchase__in=purchase_list,product__untaxed=False)
        else:
            purchase_product_list = PurchaseProduct.objects.filter(is_deleted=False, purchase__in=purchase_list)

        total_purchase = purchase_product_list.aggregate(Sum('total_amount'))['total_amount__sum']
        total_purchase = total_purchase if total_purchase else Decimal('0.00')
        
        paid_purchase = purchase_list.aggregate(Sum('paid'))['paid__sum']
        paid_purchase = paid_purchase if paid_purchase else Decimal('0.00')
        balance_purchase = purchase_list.aggregate(Sum('balance'))['balance__sum']
        balance_purchase = balance_purchase if balance_purchase else Decimal('0.00')

        expense_list = Expense.objects.filter(is_deleted=False , shop=current_shop,date__range=[start_date,end_date])

        total_expense = expense_list.aggregate(Sum('amount'))['amount__sum']
        total_expense = total_expense if total_expense else Decimal('0.00')

    context = {
    	'title':'Dashboard',
        'total_sale' : total_sale,
        'total_purchase' : total_purchase,
        'total_expense' : total_expense,
        'paid_purchase' : paid_purchase,
        'balance_purchase' : balance_purchase,
        'dashboard_active':'active'

    }
    return render(request, 'base.html', context)


def handler500(request):
    
    context = {
        'title' : "Error 500",
        "body_class":"inner error",
        "short_description" : "We're sorry! The server encountered an internal error!!!",
    }
    template = "errors/500.html"
    response = render(request,template,context)
    
    response.status_code = 500
    return response


def handler404(request):
    
    context = {
        'title' : "Error 404",
        "body_class":"inner error",
        "short_description" : "It seems we can't find what you're looking for!!!",
    }
    template = "errors/404.html"
    response = render(request,template,context)
    
    response.status_code = 404
    return response


def handler403(request):
    
    context = {
        'title' : "Error 403",
        "body_class":"inner error",
        "short_description" : "You're not authorized to view this page.",
    }
    template = "errors/403.html"
    response = render(request,template,context)
    
    response.status_code = 403
    return response


def handler400(request):
    
    context = {
        'title' : "Error 400",
        "body_class":"inner error",
        "short_description" : "Your browser sent a request that this server could not understand.",
    }
    template = "errors/400.html"
    response = render(request,template,context)
    
    response.status_code = 400
    return response


@login_required
@check_group(['admin','staff'])
def view_notifications(request):

    current_shop = get_current_shop(request)

    if not request.user.is_superuser:

        user_profile = Profile.objects.get(user=request.user)
        
        if user_profile.user_type =='admin':
            instances = Notification.objects.filter(is_deleted=False,shop=current_shop)
        else:
            instances = Notification.objects.filter(is_deleted=False,shop=current_shop,is_cheque=False)
    else:
        instances = Notification.objects.filter(is_deleted=False,shop=current_shop,is_cheque=False)


    title = "Notifications"
    
    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Notifications (%s)" % query
        instances = instances.filter(Q(message__icontains=query)|Q(product__icontains=query))


    context = {
        'title' : title,
        "instances" : instances,
    }
    return render(request,'app/view_notifications.html',context) 


@login_required
@check_group(['admin','staff'])
def mark_as_read(request,pk):
    Notification.objects.filter(pk=pk,is_deleted=False).update(is_read=True)

    return HttpResponseRedirect(reverse('app:view_notifications'))


@login_required
@check_group(['admin','staff'])
def mark_as_not_read(request,pk):
    Notification.objects.filter(pk=pk,is_deleted=False).update(is_read=False)

    return HttpResponseRedirect(reverse('app:view_notifications'))


@login_required
@check_group(['admin','staff'])
def search_result(request):
    current_shop = get_current_shop(request)
    product_instances = None
    vendor_instances = None
    customer_instances = None
    title1 = ''
    title2 = ''
    title3 = ''
    instances1 = Product.objects.filter(is_deleted=False,shop=current_shop)
    instances2 = Vendor.objects.filter(is_deleted=False,shop=current_shop)
    instances3 = Customer.objects.filter(is_deleted=False,shop=current_shop)

    query = request.GET.get("q")

    title="Search Result- (%s)" % query
    
    if query:
        title1 = "Products (%s)" % query
        title2 = "Vendors (%s)" % query
        title3 = "Customers (%s)" % query
        product_instances = instances1.filter(Q(name__icontains=query)|Q(product_id__icontains=query)|Q(unit_price__icontains=query))
        vendor_instances = instances2.filter(Q(name__icontains=query)|Q(phone__icontains=query)|Q(email__icontains=query)|Q(address__icontains=query))
        customer_instances = instances3.filter(Q(name__icontains=query)|Q(customer_id__icontains=query)|Q(phone__icontains=query)|Q(email__icontains=query)|Q(details__icontains=query))

    context = {
        "title" : title,
        'title1' : title1,
        "title2" : title2, 
        "title3" : title3,
        "product_instances" : product_instances,
        "vendor_instances" : vendor_instances,
        "customer_instances" : customer_instances
    }
    return render(request,'app/search_result.html',context) 

@login_required
@check_group(['admin','staff'])
def mark_as_deleted(request,pk):
    Notification.objects.filter(pk=pk,is_deleted=False).update(is_deleted=True)

    return HttpResponseRedirect(reverse('app:view_notifications'))
