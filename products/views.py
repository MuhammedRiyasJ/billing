from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect
import json
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from products.forms import ProductForm
from products.models import Product
from app.functions import get_current_shop, generate_form_errors
import datetime
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from users.models import Profile


@login_required
@check_group(['admin'])
def create_product(request):     
    if request.method == "POST":
        form = ProductForm(request.POST,request=request)
        untaxed = request.POST.get('untaxed',False)

        #get current shop
        shop = get_current_shop(request)

        if form.is_valid():

            untaxed = request.POST.get('untaxed',False)

            #create product_id
            product_id = 1
            product_obj = Product.objects.filter(shop=shop).order_by("-date_added")[:1]
            if product_obj.exists():
                for product in product_obj:
                    product_id = product.product_id + 1
              

            #create product
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.product_id = product_id
            data.shop = shop
            if untaxed:
                data.untaxed = True
            data.save()
            
            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('products:view_product', kwargs = {'pk' : data.pk}))
        
        else: 
            errors =generate_form_errors(form,formset=False)      
            context = {
	            "form" : form,
	            "title" : "Create Product",
                "errors" : errors,
                "products_active":"active" 
	        }          
            
        return render(request, 'products/entry_product.html', context)

    else: 
        form = ProductForm()
        
        
        context = {
            "form" : form,
            "title" : "Create Product",
            "url" : reverse('products:create_product'),
            "products_active":"active" 
        }
        return render(request, 'products/entry_product.html', context)


@login_required
@check_group(['admin'])
def edit_product(request,pk):
    instance = get_object_or_404(Product.objects.filter(pk=pk,is_deleted=False))
    
    if request.method == "POST":
        response_data = {}  
        form = ProductForm(request.POST,instance=instance,request=request,edit=True)
        untaxed = request.POST.get('untaxed',False)
        if untaxed:
            untaxed = True
        
        if form.is_valid(): 
            
            #update product
            data = form.save(commit=False)
            data.updater = request.user
            data.date_updated = datetime.datetime.now()
            data.untaxed = untaxed
            data.save()
            
            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('products:view_product', kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Update Product",
                "errors" : errors,
                "products_active":"active" 
            }          
            
        return render(request, 'products/entry_product.html', context)

    else: 
        form = ProductForm(instance=instance)
        
        context = {
            "form" : form,
            "title" : "Edit product : " + instance.name,
            "instance" : instance,
            "url": reverse('products:edit_product', kwargs = {'pk' : instance.pk}),
            "products_active":"active" 
        }
        return render(request, 'products/entry_product.html', context)
      

@login_required
@check_group(['admin','staff'])
def view_products(request):
    current_shop = get_current_shop(request)
    user_profile = Profile.objects.get(user=request.user)

    if user_profile.tax_only:
        instances = Product.objects.filter(is_deleted=False,shop=current_shop,untaxed=False)
    else:
        instances = Product.objects.filter(is_deleted=False,shop=current_shop)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    title = "Products"
    
    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Products (%s)" % query
        instances = instances.filter(Q(name__icontains=query)|Q(product_id__icontains=query)|Q(unit_price__icontains=query))

    #code for pagination
    paginator = Paginator(instances,100)
    page = request.GET.get('page')

    try:
        instances = paginator.page(page)
    except PageNotAnInteger:
        instances = paginator.page(1)
    except EmptyPage:
        instances = paginator.page(paginator.num_pages)

    context = {
        'title' : title,
        "instances" : instances,
        'query':query,
        "message" : message,
        "products_active":"active" 
    }
    return render(request,'products/view_products.html',context) 



@login_required
@check_group(['admin','staff'])
def view_product(request,pk):
    instance = get_object_or_404(Product.objects.filter(pk=pk,is_deleted=False))

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    context = {
        "instance" : instance,
        "message": message,
        "title" : "Product : " + str(instance.product_id),
        "products_active":"active" 
    }
    return render(request,'products/view_product.html',context)


@login_required
@check_group(['admin'])
def delete_product(request,pk):
    instance = get_object_or_404(Product.objects.filter(pk=pk))
    Product.objects.filter(pk=pk).update(is_deleted=True)
    
    request.session['message'] = 'Successfully Deleted'
    return HttpResponseRedirect(reverse('products:view_products'))


@login_required
@check_group(['admin'])
def create_product_popup(request):

    if request.method == "POST":
        current_shop = get_current_shop(request)
        form = ProductForm(request.POST,request=request)
        untaxed = request.POST.get('untaxed',False)
        if untaxed:
            untaxed = True
            
        if form.is_valid():

            #create product_id
            product_id = 1
            product_obj = Product.objects.filter(shop=current_shop).order_by("-date_added")[:1]
            if product_obj.exists():
                for product in product_obj:
                    product_id = product.product_id + 1
            
            #get current shop
            print request
            shop = get_current_shop(request)  

            #create product
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.product_id = product_id
            data.shop = shop
            data.untaxed = untaxed
            data.save()

            response_data = {
                'status':'true',
                'message': "Product %s Created Successfully" %(data.name),
            }
            
            response = HttpResponse(json.dumps(response_data), content_type='application/javascript')
            return response
        
        else:
            errors = generate_form_errors(form,formset=False)

            response_data = {
                'status':'false',
                'message': errors,
            }
            response = HttpResponse(json.dumps(response_data), content_type='application/javascript')  
            return response