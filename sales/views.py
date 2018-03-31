from django.contrib.auth.decorators import login_required
from sales.forms import SaleForm, SaleProductForm
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
import json
from django.shortcuts import render, get_object_or_404
import datetime
from django.db.models import Q
from sales.models import Sale, SaleProduct
from products.models import Product
from customers.models import Customer
from customers.forms import CustomerForm
from app.functions import get_current_shop, generate_form_errors
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
from django.forms.models import inlineformset_factory
from django.forms.widgets import Select, TextInput
from app.functions import create_notification
from dal import autocomplete
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from users.models import Profile
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _


@login_required
@check_group(['admin','staff'])
def create_sale(request):   
    SaleProductFormset = formset_factory(SaleProductForm,min_num=1,validate_min=True,extra=0)
    current_shop = get_current_shop(request)
    customer_form = CustomerForm()

    if request.method == "POST":

        form = SaleForm(request.POST)

        sale_product_formset = SaleProductFormset(request.POST,prefix='sale_product_formset')
        for field in sale_product_formset:
            field.fields['product'].queryset = Product.objects.filter(shop=current_shop,is_deleted=False)
        
        if form.is_valid() and sale_product_formset.is_valid(): 
            
            sale_id = 'OFF/1'
            sale_obj = Sale.objects.filter(shop=current_shop).order_by("-date_added")[:1]
            if sale_obj:
                for sale in sale_obj:
                    sale_id = 'OFF/'+str(int(re.findall(r'\d+', sale.sale_id )[0]) + 1)
                     
            
            error_messages = ''
            #check product availability
            for f in sale_product_formset:
                product = f.cleaned_data['product']
                quantity = f.cleaned_data['quantity']

                available_stock = 0
                
                #check product availability
                if Product.objects.filter(shop=current_shop,pk=product.pk).exists():
                    available_stock = Product.objects.get(shop=current_shop,pk=product.pk).stock
                if available_stock < quantity:
                    error_messages += "%s is out of stock. Only %s unit(s) exists in %s . </br >" % (product,available_stock,current_shop)
                
            if not error_messages:
 
                customer = form.cleaned_data['customer'] 

                #create sale
                data = form.save(commit=False)
                data.creator = request.user
                data.updater = request.user
                data.sale_id = sale_id
                data.shop = current_shop
                data.date_added = datetime.datetime.now()
                data.save()

                #save SaleProduct
                for form in sale_product_formset:
                    product = form.cleaned_data['product']
                    unit_price = form.cleaned_data['unit_price']
                    quantity = form.cleaned_data['quantity']
                    offer = form.cleaned_data['offer']
                    output_gst = form.cleaned_data['output_gst']
                    tax_amount = form.cleaned_data['tax_amount']
                    amount = form.cleaned_data['amount']
                    total_amount = form.cleaned_data['total_amount']
                    SaleProduct(      
                        product = product,
                        sale = data,
                        unit_price = unit_price,
                        quantity = quantity,
                        output_gst = output_gst,
                        offer = offer,
                        tax_amount =tax_amount,
                        amount = amount,
                        total_amount = total_amount
                    ).save()

                    current_stock =  Product.objects.get(pk=product.pk,shop=current_shop).stock
                    updated_stock = current_stock - quantity
                    Product.objects.filter(pk=product.pk,shop=current_shop).update(stock=updated_stock)

                    if updated_stock == 0:
                        create_notification(product,current_shop)

                request.session['message'] = 'Form Submitted successfully'
                return HttpResponseRedirect(reverse('sales:view_sale', kwargs = {'pk' : data.pk}))
            else:   
                context = {
                    "form" : form,
                    "customer_form" : customer_form,
                    "title" : "Create Sale",
                    "sale_product_formset" : sale_product_formset,
                    "errors" : error_messages,
                    "sales_active":"active"
                }            
                return render(request, 'sales/entry_sale.html', context)
        else:
            errors =generate_form_errors(form,formset=False) 
            errors += generate_form_errors(sale_product_formset,formset=True)     
            context = {
	            "form" : form,
                "customer_form" : customer_form,
	            "title" : "Create Sale",
                "sale_product_formset" : sale_product_formset,
                "errors" : errors,
                "sales_active":"active"
	        }            
            return render(request, 'sales/entry_sale.html', context) 

    else: 
        form = SaleForm()
        sale_product_formset = SaleProductFormset(prefix='sale_product_formset')

        context = {
            "form" : form,
            "customer_form" : customer_form,
            "title" : "Create Sale",
            "sale_product_formset" : sale_product_formset,
            "url" : reverse('sales:create_sale'),
            "sales_active":"active"
        }
        return render(request, 'sales/entry_sale.html', context)
    

@login_required
@check_group(['admin','staff'])
def edit_sale(request,pk):
    current_shop = get_current_shop(request)
    instance = get_object_or_404(Sale.objects.filter(pk=pk,is_deleted=False))
    customer_form = CustomerForm()
        
    SaleProductFormset = inlineformset_factory(
                                              Sale,
                                              SaleProduct, 
                                              can_delete=True,
                                              extra=0,
                                              min_num=1,
                                              validate_min=True,
                                              exclude=('shop','sale'),
                                              widgets = {
                                                    'product': autocomplete.ModelSelect2(url='products:product-autocomplete',attrs={'data-placeholder': '*Select Product','data-minimum-input-length': 1}),
                                                    'quantity' : TextInput(attrs={'placeholder': '*Enter quantity','class':'required form-control'}),
                                                    'unit_price' : TextInput(attrs={'placeholder': 'Enter unit price(inc. tax)','label': '*Unit price','class':'required form-control'}),
                                                    'output_gst' : TextInput(attrs={'placeholder': 'Output GST','class': 'required form-control'}),
                                                    'offer' : TextInput(attrs={'placeholder': 'Enter Discount','class':'required form-control'}),
                                                    'amount' : TextInput(attrs={'placeholder': 'Enter amount','class':'required form-control'}),
                                                    'tax_amount' : TextInput(attrs={'placeholder': 'Tax amount','class':'required form-control'}),
                                                    'total_amount' : TextInput(attrs={'placeholder': 'Enter total amount','class':'required form-control'}),
                                                },
                                                error_messages = {
                                                    'product' : {
                                                        'required' : _("Product field is required."),
                                                    },
                                                    'unit_price' : {
                                                        'required' : _("Unit Price field is required."),
                                                    },
                                                    'quantity' : {
                                                        'required' : _("Quantity field is required."),
                                                    },             
                                                }
                                            )
    
    if request.method == "POST":
        form = SaleForm(request.POST,instance=instance)
        sale_product_formset = SaleProductFormset(request.POST,prefix='sale_product_formset',instance=instance)
        
        error_messages = ''

        if form.is_valid() and sale_product_formset.is_valid(): 
            

            #check product availability
            for f in sale_product_formset:
                product = f.cleaned_data['product']
                quantity = f.cleaned_data['quantity']

                # previous sale quantity taken
                if SaleProduct.objects.filter(pk=f.instance.pk).exists():
                    saleform = SaleProduct.objects.get(pk=f.instance.pk)
                    pre_product = saleform.product
                    pre_quantity = saleform.quantity

                    if pre_product == product:
                        available_stock = Product.objects.get(shop=current_shop,pk=product.pk).stock
                        new_stock = available_stock + pre_quantity
                        if new_stock < quantity:
                            error_messages += "%s is out of stock. Only %s unit(s) exists. </br >" % (product,available_stock)
                    else:
                        available_stock = Product.objects.get(shop=current_shop,pk=product.pk).stock
                        if available_stock < quantity:
                            error_messages += "%s is out of stock. Only %s unit(s) exists. </br >" % (product,available_stock)
                    
                else:
                    available_stock = 0

                    #check product availability
                    if product:
                        available_stock = Product.objects.get(shop=current_shop,pk=product.pk).stock
                    if available_stock < quantity:
                        error_messages += "%s is out of stock. Only %s unit(s) exists. </br >" % (product,available_stock)
            if not error_messages:

                #update item
                data = form.save(commit=False)
                data.updater = request.user
                data.date_updated = datetime.datetime.now()
                data.save()

                if sale_product_formset.deleted_forms:
                    for deleted_form in sale_product_formset.deleted_forms:
                        new_stock = deleted_form.instance.product.stock + deleted_form.instance.quantity
                        Product.objects.filter(pk=deleted_form.instance.product.pk, is_deleted=False).update(stock=new_stock)

                #save SaleProduct
                for form in sale_product_formset:
                    product = form.cleaned_data['product']
                    unit_price = form.cleaned_data['unit_price']
                    quantity = form.cleaned_data['quantity']
                    offer = form.cleaned_data['offer']
                    output_gst = form.cleaned_data['output_gst']
                    tax_amount = form.cleaned_data['tax_amount']
                    amount = form.cleaned_data['amount']

                    # previous sale quantity taken
                    if SaleProduct.objects.filter(pk=form.instance.pk).exists():
                        saleform = SaleProduct.objects.get(pk=form.instance.pk)
                        pre_product = saleform.product
                        pre_quantity = saleform.quantity

                        if pre_product == product:
                            current_stock =  Product.objects.get(pk=product.pk,shop=current_shop).stock
                            Product.objects.filter(pk=product.pk,shop=current_shop).update(stock=current_stock + pre_quantity - quantity)
                        else:
                            current_stock =  pre_product.stock
                            Product.objects.filter(pk=pre_product.pk,shop=current_shop).update(stock= current_stock + pre_quantity)
                            current_product_stock = product.stock
                            product.stock = current_product_stock - quantity
                            product.save()

                    else:
                        current_stock =  Product.objects.get(pk=product.pk,shop=current_shop).stock
                        Product.objects.filter(pk=product.pk,shop=current_shop).update(stock= current_stock - quantity)

                #update sale product fomset forms
                sale_product_formset.save()
                   
                request.session['message'] = 'Form Submitted successfully'
                return HttpResponseRedirect(reverse('sales:view_sale', kwargs = {'pk' : data.pk}))

            else:
                context = {
                    "form" : form,
                    "customer_form" : customer_form,
                    "title" : "Edit Sale : "+instance.sale_id,
                    "sale_product_formset" : sale_product_formset,
                    "errors" : error_messages,
                    "sales_active":"active"
                }            
                return render(request, 'sales/entry_sale.html', context)

        else:
            error_messages = generate_form_errors(form, formset=False)
            error_messages += generate_form_errors(sale_product_formset, formset=True)
            context = {
                "form" : form,
                "customer_form" : customer_form,
                "title" : "Edit Sale : "+instance.sale_id,
                "sale_product_formset" : sale_product_formset,
                "errors" : error_messages,
                "sales_active":"active"
            }            
            return render(request, 'sales/entry_sale.html', context)

    else:
        form = SaleForm(instance=instance) 
        sale_product_formset = SaleProductFormset(prefix='sale_product_formset',instance=instance)
        for field in sale_product_formset:
            field.fields['product'].queryset = Product.objects.filter(shop=current_shop,is_deleted=False)

        context = {
            "form" : form,
            "customer_form" : customer_form,
            "sale_product_formset" : sale_product_formset,
            "title" : "Edit Sale : "+instance.sale_id,
            "url": reverse('sales:edit_sale', kwargs = {'pk' : instance.pk}),
            "sales_active":"active"
        }
        return render(request, 'sales/entry_sale.html', context)


@login_required
@check_group(['admin','staff'])
def view_sales(request):
    current_shop = get_current_shop(request)
    instances = Sale.objects.filter(is_deleted=False,shop=current_shop)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None
    
    title = "Sales"

    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Sales (%s)" % query
        try:
            date_query = datetime.datetime.strptime(query,"%d-%m-%y")
        except:
            date_query = query
        instances = instances.filter(Q(customer__name__icontains=query)|Q(sale_id__icontains=query)|Q(date__icontains=date_query))

    #code for page nation starts here
    paginator = Paginator(instances, 100)
    page = request.GET.get('page')

    try:
        instances = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        instances = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        instances = paginator.page(paginator.num_pages)
    
    context = {
        'title' : title,
        "instances" : instances,
        'query':query,
        "message" : message,
        "sales_active":"active"
    }
    return render(request,'sales/view_sales.html',context) 


@login_required
@check_group(['admin','staff'])
def view_sale(request,pk):
    user_profile = Profile.objects.get(user=request.user)
    instance = get_object_or_404(Sale.objects.filter(pk=pk,is_deleted=False))

    sale_list = []
    if user_profile.tax_only:
       sale_products = SaleProduct.objects.filter(sale=instance,is_deleted=False,product__untaxed=False)

    else:
        sale_products = SaleProduct.objects.filter(sale=instance,is_deleted=False)

    total_discount = sale_products.aggregate(Sum('offer'))['offer__sum']
    sale_list.append(total_discount)

    total_net_amount =sale_products.aggregate(Sum('amount'))['amount__sum']
    sale_list.append(total_net_amount)

    total_tax_amount = sale_products.aggregate(Sum('tax_amount'))['tax_amount__sum']
    sale_list.append(total_tax_amount)

    total = sale_products.aggregate(Sum('total_amount'))['total_amount__sum']
    sale_list.append(total)
    
    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    context = {
        "instance" : instance,
        "title" : "Sale : " + str(instance.sale_id),
        "sale_products" : sale_products,
        "sale_list":sale_list,
        "message" : message,
        "sales_active":"active"
    }
    return render(request,'sales/view_sale.html',context)


@login_required
@check_group(['admin','staff'])
def delete_sale(request,pk):
    current_shop = get_current_shop(request)
    instance = get_object_or_404(Sale.objects.filter(pk=pk,is_deleted=False,shop=current_shop))
    sale_products = SaleProduct.objects.filter(sale=instance,is_deleted=False)

    #update product stock
    for sale_product in sale_products:
        stock=Product.objects.get(pk=sale_product.product.pk,shop=current_shop).stock
        Product.objects.filter(pk=sale_product.product.pk,shop=current_shop).update(stock=stock+sale_product.quantity)

    
    Sale.objects.filter(pk=pk,shop=current_shop).update(is_deleted=True)
    sale_products.update(is_deleted=True)
    
    request.session['message'] = 'Successfully Deleted'
    return HttpResponseRedirect(reverse('sales:view_sales'))


@login_required
@check_group(['admin','staff'])
def print_sale_8b(request,pk):
    user_profile = Profile.objects.get(user=request.user)
    instance = get_object_or_404(Sale.objects.filter(pk=pk,is_deleted=False))

    if user_profile.tax_only:
       sale_products = SaleProduct.objects.filter(sale=pk,is_deleted=False,product__untaxed=False)

    else:
        sale_products = SaleProduct.objects.filter(sale=pk,is_deleted=False)

    total_price = sale_products.aggregate(Sum('unit_price'))['unit_price__sum']
    total_quantity = sale_products.aggregate(Sum('quantity'))['quantity__sum']
    total_offer = sale_products.aggregate(Sum('offer'))['offer__sum']
    total_net_amount = sale_products.aggregate(Sum('amount'))['amount__sum']
    total_tax_amount = sale_products.aggregate(Sum('tax_amount'))['tax_amount__sum']

    total_gross_value = 0
    for sale_product in sale_products:

        value = sale_product.unit_price * sale_product.quantity
        output_gst = sale_product.output_gst if sale_product.output_gst else Decimal('0.0')
        gross_value = value + value * output_gst/100
        total_gross_value += gross_value

    
    context = {
        "instance" : instance,
        "sale_products" : sale_products,
        "total_price":total_price,
        "total_quantity":total_quantity,
        "total_gross_value":total_gross_value,
        "total_offer": total_offer,
        "total_net_amount":total_net_amount,
        "total_tax_amount":total_tax_amount,
        "title" : "Sale : " + str(instance.sale_id),
        "sale_active" : "active"
    }
    return render(request,'sales/print_sale_8b.html',context)


@login_required
@check_group(['admin','staff'])
def print_sale_8(request,pk):
    user_profile = Profile.objects.get(user=request.user)
    instance = get_object_or_404(Sale.objects.filter(pk=pk,is_deleted=False))

    if user_profile.tax_only:
       sale_products = SaleProduct.objects.filter(sale=pk,is_deleted=False,product__untaxed=False)

    else:
        sale_products = SaleProduct.objects.filter(sale=pk,is_deleted=False)

    total_price = sale_products.aggregate(Sum('unit_price'))['unit_price__sum']
    total_quantity = sale_products.aggregate(Sum('quantity'))['quantity__sum']
    total_offer = sale_products.aggregate(Sum('offer'))['offer__sum']
    total_net_amount = sale_products.aggregate(Sum('amount'))['amount__sum']
    total_tax_amount = sale_products.aggregate(Sum('tax_amount'))['tax_amount__sum']

    total_gross_value = 0
    for sale_product in sale_products:

        value = sale_product.unit_price * sale_product.quantity
        output_gst = sale_product.output_gst if sale_product.output_gst else Decimal('0.0')
        gross_value = value + value * output_gst/100
        total_gross_value += gross_value


    
    context = {
        "instance" : instance,
        "sale_products" : sale_products,
        "total_price":total_price,
        "total_quantity":total_quantity,
        "total_gross_value":total_gross_value,
        "total_offer": total_offer,
        "total_net_amount":total_net_amount,
        "total_tax_amount":total_tax_amount,
        "title" : "Sale : " + str(instance.sale_id),
        "sale_active" : "active"
    }
    return render(request,'sales/print_sale_8.html',context)


@login_required
def get_unit_price(request):
    pk = request.GET.get('id')

    if Product.objects.filter(pk=pk).exists():
        item = Product.objects.get(pk=pk)  
        response_data = {
            "status" : "true",
            'pk' : str(item.pk),
            'unit_price' : str(item.unit_price),
            'output_gst' : str(item.output_gst)
        }
    else:
        response_data = {
            "status" : "false",
            "message" : "Product not found"
        }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')

