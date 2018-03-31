from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
import json
from django.shortcuts import render, get_object_or_404
import datetime
from django.db.models import Q
from purchases.models import Purchase, PurchaseProduct
from app.functions import get_current_shop, generate_form_errors
from django.forms.formsets import formset_factory
from purchases.forms import PurchaseProductForm, PurchaseForm
from products.models import Product
from vendors.models import Vendor
from vendors.forms import VendorForm
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
from django.forms.models import inlineformset_factory
from django.forms.widgets import Select, TextInput
from purchases.functions import remove_previous_product_stock
from dal import autocomplete
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from users.models import Profile
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _


@login_required
@check_group(['admin'])
def create_purchase(request):  
    PurchaseProductFormset = formset_factory(PurchaseProductForm,min_num=1,validate_min=True,extra=0)
    current_shop = get_current_shop(request)
    vendor_form = VendorForm()

    if request.method == "POST":
        form = PurchaseForm(request.POST)

        purchase_product_formset = PurchaseProductFormset(request.POST,prefix='purchase_product_formset')
        for field in purchase_product_formset:
            field.fields['product'].queryset = Product.objects.filter(shop=current_shop,is_deleted=False)
        
        if form.is_valid() and purchase_product_formset.is_valid(): 
            
            purchase_id = 'P1'
            purchase_obj = Purchase.objects.filter(shop=current_shop).order_by("-date_added")[:1]
            if purchase_obj:
                for purchase in purchase_obj:
                    purchase_id = 'P'+str(int(re.findall(r'\d+', purchase.purchase_id)[0]) + 1)
            
            balance = form.cleaned_data['balance'] 
            vendor = form.cleaned_data['vendor']

            #create purchase
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.purchase_id = purchase_id
            data.shop = current_shop
            data.date_added = datetime.datetime.now()
            data.save()

            #save PurchaseProduct
            for form in purchase_product_formset:
                product = form.cleaned_data['product']
                unit_cost = form.cleaned_data['unit_cost']
                input_gst = form.cleaned_data['input_gst']
                quantity = form.cleaned_data['quantity']
                offer = form.cleaned_data['offer']
                tax_amount = form.cleaned_data['tax_amount']
                amount = form.cleaned_data['amount']
                total_amount = form.cleaned_data['total_amount']

                PurchaseProduct(      
                    product = product,
                    purchase = data,
                    unit_cost = unit_cost,
                    input_gst = input_gst,
                    quantity = quantity,
                    offer = offer,
                    tax_amount =tax_amount,
                    amount = amount,
                    total_amount = total_amount
                ).save()

                if Product.objects.filter(pk=product.pk,shop=current_shop).exists():
                        current_stock =  Product.objects.get(pk=product.pk,shop=current_shop).stock
                        Product.objects.filter(pk=product.pk,shop=current_shop).update(stock=quantity + current_stock)
            
            #update balance of vendor
            if vendor:
                current_balance =  Vendor.objects.get(pk=vendor.pk,shop=current_shop,is_deleted=False).balance
                Vendor.objects.filter(pk=vendor.pk,shop=current_shop,is_deleted=False).update(balance= current_balance + balance)

            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('purchases:view_purchase', kwargs = {'pk' : data.pk}))

        else:
            errors =generate_form_errors(form,formset=False)
            errors +=generate_form_errors(purchase_product_formset,formset=True)
            context = {
                "form" : form,
                "vendor_form" : vendor_form,
                "title" : "Create Purchase",
                "purchase_product_formset" : purchase_product_formset,
                "errors" : errors,
                "purchases_active":"active"
            }          
            
        return render(request, 'purchases/entry_purchase.html', context)       

    else: 
        form = PurchaseForm()
        
        purchase_product_formset = PurchaseProductFormset(prefix='purchase_product_formset')
        for field in purchase_product_formset:
            field.fields['product'].queryset = Product.objects.filter(shop=current_shop,is_deleted=False)
        
        context = {
            "form" : form,
            "vendor_form" : vendor_form,
            "purchase_product_formset" : purchase_product_formset,
            "title" : "Create Purchase",
            "url" : reverse('purchases:create_purchase'),
            "purchases_active":"active"
        }
        return render(request, 'purchases/entry_purchase.html', context)
    


@login_required
@check_group(['admin'])
def edit_purchase(request,pk):
    current_shop = get_current_shop(request)
    purchase_instance = get_object_or_404(Purchase.objects.filter(pk=pk,is_deleted=False,shop=current_shop))
    vendor_form = VendorForm()

    PurchaseProductFormset = inlineformset_factory(
                                              Purchase,
                                              PurchaseProduct, 
                                              can_delete=True,
                                              extra=0,
                                              min_num=1,
                                              validate_min=True,
                                              exclude=('shop','purchase'),
                                              widgets = {
                                                    'product': autocomplete.ModelSelect2(url='products:product-autocomplete',attrs={'data-placeholder': 'Select Product','data-minimum-input-length': 1}),
                                                    'quantity' : TextInput(attrs={'placeholder': 'Enter quantity','class':'required form-control'}),
                                                    'unit_cost' : TextInput(attrs={'placeholder': 'Enter unit cost(inc. tax)','label': 'Unit cost','class':'required form-control'}),
                                                    'input_gst' : TextInput(attrs={'placeholder': 'Input Tax','class': 'required form-control'}),
                                                    'offer' : TextInput(attrs={'placeholder': 'Enter offer','class':'required form-control'}),
                                                    'amount' : TextInput(attrs={'placeholder': 'Enter amount','class':'required form-control'}),
                                                    'tax_amount' : TextInput(attrs={'placeholder': 'Tax amount','class':'required form-control'}),
                                                    'total_amount' : TextInput(attrs={'placeholder': 'Enter total amount','class':'required form-control'}),
                                                },
                                              error_messages={
                                                'product': {
                                                    'required': _("product field is required."),
                                                },
                                                'unit_cost': {
                                                    'required': _("Unit Cost field is required."),
                                                },
                                                'quantity': {
                                                    'required': _("Quantity field is required."),
                                                },
                                              }
                                            )
    
    if request.method == "POST":
        response_data = {}  
        form = PurchaseForm(request.POST,instance=purchase_instance)
        purchase_product_formset = PurchaseProductFormset(request.POST,prefix='purchase_product_formset',instance=purchase_instance)
        
        error = ''
        
        # checking quantity and stock  of deleted product to ensure quantity is less than stock
        if purchase_product_formset.deleted_forms:
            for deleted_form in purchase_product_formset.deleted_forms:
                if deleted_form.instance.product.stock <= deleted_form.instance.quantity:
                    error = "Invalid operation, Product can not removed because of incorrect quantity"

        #tacking vendor and vendor balance in variables
        vendor_balance = purchase_instance.balance
        vendor = purchase_instance.vendor

        if form.is_valid() and purchase_product_formset.is_valid():

            #remove previous  Purchase Product
            purchase_product = PurchaseProduct.objects.filter(purchase=purchase_instance.pk,is_deleted=False)
            for purchase_product_form in purchase_product_formset:
                new_product = purchase_product_form.cleaned_data['product']
                new_quantity = purchase_product_form.cleaned_data['quantity']
                new_unit_cost = purchase_product_form.cleaned_data['unit_cost']
                new_input_gst = purchase_product_form.cleaned_data['input_gst']
                new_offer = purchase_product_form.cleaned_data['offer']
                new_amount = purchase_product_form.cleaned_data['amount']
                
                pre_quantity = 0
                pre_product = None
                if PurchaseProduct.objects.filter(pk=purchase_product_form.instance.pk).exists():
                    purchaseform = PurchaseProduct.objects.get(pk=purchase_product_form.instance.pk)
                    pre_quantity = purchaseform.quantity
                    pre_purchase_product = PurchaseProduct.objects.get(pk=purchase_product_form.instance.pk)
                    pre_product = pre_purchase_product.product

                
                    current_stock = new_product.stock
                    new_stock =0
                    if pre_product == new_product:
                        new_stock = current_stock - pre_quantity + new_quantity
                    else:

                        if pre_product:
                            pre_product_stock_defference = pre_product.stock - pre_purchase_product.quantity

                            if pre_product_stock_defference < 0:
                                error += "You can not change product because you already sold some unit %s belong to this purchase" % pre_product.name

                    if new_quantity < 0:
                        error += "Can't change the quantity as you entered. Please re enter the quantity of %s" % (new_product)

                    if new_stock < 0:
                        error += "You can not change product because you already sold some unit %s belong to this purchase" % pre_product.name


            if not error:
                #take edited vendor and balance
                edited_balance = form.cleaned_data['balance'] 
                edited_vendor = form.cleaned_data['vendor']

                #removing deleted form from formset group and reducing count of product in stock count
                if purchase_product_formset.deleted_forms:
                    for deleted_form in purchase_product_formset.deleted_forms:
                        if deleted_form.instance.product.stock >= deleted_form.instance.quantity:
                            new_stock = deleted_form.instance.product.stock - deleted_form.instance.quantity
                            Product.objects.filter(pk=deleted_form.instance.product.pk,is_deleted=False).update(stock=new_stock)

                #update item
                data = form.save(commit=False)
                data.updater = request.user
                data.date_updated = datetime.datetime.now()
                data.save()

                #update PurchaseProduct
                for form in purchase_product_formset:
                    product = form.cleaned_data['product']
                    unit_cost = form.cleaned_data['unit_cost']
                    input_gst = form.cleaned_data['input_gst']
                    quantity = form.cleaned_data['quantity']
                    offer = form.cleaned_data['offer']
                    amount = form.cleaned_data['amount']

                    #update product stock 
                    pre_quantity = 0
                    pre_product = None
                    if PurchaseProduct.objects.filter(pk=form.instance.pk).exists():
                        purchaseform_instance = PurchaseProduct.objects.get(pk=form.instance.pk)
                        pre_quantity = purchaseform_instance.quantity
                        pre_purchase_product = purchaseform_instance
                        pre_product = pre_purchase_product.product


                    """update product stock if previous product is current product or previous product"""
                    if pre_product == product:
                        new_stock = pre_product.stock - pre_quantity + quantity
                        Product.objects.filter(pk=product.pk,shop=current_shop).update(stock=new_stock)

                    elif pre_product:
                        #reducing entire quantity from product
                        prev_product_stock = pre_product.stock - pre_quantity
                        #updating previous product stock
                        Product.objects.filter(pk=pre_product.pk,shop=current_shop).update(stock=prev_product_stock)
                        #adding newly entered quantity to product stock
                        new_stock = product.stock + quantity
                        #updating new stock
                        Product.objects.filter(pk=product.pk,shop=current_shop).update(stock=new_stock)

                        """if there is no previous product then modifing product stock"""
                    else:
                        #adding new quantity to stock
                        new_stock = product.stock + quantity
                        #updating new quantity
                        Product.objects.filter(pk=product.pk,shop=current_shop).update(stock=new_stock)


                #update purchase product fomset forms
                purchase_product_formset.save()

                #update vendor balance
                if vendor==edited_vendor:
                    if vendor:
                        current_balance =  Vendor.objects.get(pk=vendor.pk,shop=current_shop).balance
                        Vendor.objects.filter(pk=vendor.pk,shop=current_shop).update(balance= current_balance - vendor_balance + edited_balance)
                else:
                    #update new vendor balance
                    if edited_vendor:
                        current_balance =  Vendor.objects.get(pk=edited_vendor.pk,shop=current_shop).balance
                        Vendor.objects.filter(pk=edited_vendor.pk,shop=current_shop).update(balance= current_balance + edited_balance )
                    #remove previous vendor balance
                    if vendor:
                        pre_balance =  Vendor.objects.get(pk=vendor.pk,shop=current_shop).balance
                        Vendor.objects.filter(pk=vendor.pk,shop=current_shop).update(balance= pre_balance - vendor_balance )

                    
            else:
                context = {
                    "form" : form,
                    "vendor_form" : vendor_form,
                    "errors" : error,
                    "purchase_product_formset" : purchase_product_formset,
                    "title" : "Edit Purchase : "+purchase_instance.purchase_id,
                    "purchase_active":"active"
                }          
                return render(request, 'purchases/entry_purchase.html', context)

            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('purchases:view_purchase', kwargs = {'pk' : data.pk}))


        else:
            errors =generate_form_errors(form,formset=False)
            errors +=generate_form_errors(purchase_product_formset,formset=True)
            context = {
                "form" : form,
                "vendor_form" : vendor_form,
                "errors" : errors,
                "purchase_product_formset" : purchase_product_formset,
                "title" : "Edit Purchase : "+ purchase_instance.purchase_id,
                "purchase_active":"active"
            }          
            
        return render(request, 'purchases/entry_purchase.html', context)

    else:
        form = PurchaseForm(instance=purchase_instance) 
        purchase_product_formset = PurchaseProductFormset(prefix='purchase_product_formset',instance=purchase_instance)
        for field in purchase_product_formset:
            field.fields['product'].queryset = Product.objects.filter(shop=current_shop,is_deleted=False)

        context = {
            "form" : form,
            "vendor_form" : vendor_form,
            "purchase_product_formset" : purchase_product_formset,
            "title" : "Edit Purchase : "+purchase_instance.purchase_id,
            "url": reverse('purchases:edit_purchase', kwargs = {'pk' : purchase_instance.pk}),
            "purchases_active":"active"
        }
        return render(request, 'purchases/entry_purchase.html', context)

        
@login_required
@check_group(['admin'])
def view_purchases(request):
    current_shop = get_current_shop(request)
    instances = Purchase.objects.filter(is_deleted=False,shop=current_shop)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None
    
    title = "Purchases"

    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Purchases (%s)" % query
        try:
            date_query = datetime.datetime.strptime(query,"%d-%m-%y")
        except:
            date_query = query
        instances = instances.filter(Q(vendor__name__icontains=query)|Q(purchase_id__icontains=query)|Q(date__icontains=date_query))

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
        "purchases_active":"active"
    }
    return render(request,'purchases/view_purchases.html',context) 


@login_required
@check_group(['admin'])
def view_purchase(request,pk):
    user_profile = Profile.objects.get(user=request.user)
    instance = get_object_or_404(Purchase.objects.filter(pk=pk,is_deleted=False))

    purchase_list = []
    if user_profile.tax_only:
       purchase_products = PurchaseProduct.objects.filter(purchase=instance,is_deleted=False,product__untaxed=False)

    else:
        purchase_products = PurchaseProduct.objects.filter(purchase=instance,is_deleted=False)

    total_discount = purchase_products.aggregate(Sum('offer'))['offer__sum']
    purchase_list.append(total_discount)

    total_net_amount =purchase_products.aggregate(Sum('amount'))['amount__sum']
    purchase_list.append(total_net_amount)

    total_tax_amount = purchase_products.aggregate(Sum('tax_amount'))['tax_amount__sum']
    purchase_list.append(total_tax_amount)

    total = purchase_products.aggregate(Sum('total_amount'))['total_amount__sum']
    purchase_list.append(total)
    
    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    context = {
        "instance" : instance,
        "purchase_products" : purchase_products,
        "title" : "Purchase : " + str(instance.purchase_id),
        "message" : message,
        "purchase_list":purchase_list,
        "purchases_active":"active"
    }
    return render(request,'purchases/view_purchase.html',context)


@login_required
@check_group(['admin'])
def delete_purchase(request,pk):
    current_shop = get_current_shop(request)
    instance = get_object_or_404(Purchase.objects.filter(pk=pk,is_deleted=False,shop=current_shop))
    purchase_products = PurchaseProduct.objects.filter(purchase=instance,is_deleted=False)

    #update product stock
    for purchase_product in purchase_products:
        stock=Product.objects.get(pk=purchase_product.product.pk,shop=current_shop).stock
        Product.objects.filter(pk=purchase_product.product.pk,shop=current_shop).update(stock=stock-purchase_product.quantity)

    #update vendor balance
    if instance.vendor:
        balance=Vendor.objects.get(pk=instance.vendor.pk,shop=current_shop,is_deleted=False).balance
        Vendor.objects.filter(pk=instance.vendor.pk,shop=current_shop,is_deleted=False).update(balance=balance-instance.balance)
    
    Purchase.objects.filter(pk=pk,shop=current_shop).update(is_deleted=True)
    
    request.session['message'] = 'Successfully Deleted'
    return HttpResponseRedirect(reverse('purchases:view_purchases'))


@login_required
@check_group(['admin'])
def get_input_tax(request):
    pk = request.GET.get('id')
    print pk
    if Product.objects.filter(pk=pk).exists():
        item = Product.objects.get(pk=pk)  
        response_data = {
            "status" : "true",
            'input_gst' : str(item.input_gst),
        }
    else:
        response_data = {
            "status" : "false",
            "message" : "Product not found"
        }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')
