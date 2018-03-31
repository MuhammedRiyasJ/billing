from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect
import json
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from customers.forms import CustomerForm
from customers.models import Customer
from app.functions import get_current_shop, generate_form_errors
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
@check_group(['admin'])
def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST,request=request)
            
        if form.is_valid():

            #get current shop
            shop = get_current_shop(request) 

            #create customer_id
            customer_id = 1
            customer_obj = Customer.objects.filter(shop=shop).order_by("-date_added")[:1]
            if customer_obj:
                for customer in customer_obj:
                    customer_id = customer.customer_id + 1

            #create farmer
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.customer_id = customer_id
            data.shop = shop
            data.save()
            
            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('customers:view_customer', kwargs = {'pk' : data.pk}))
        
        else:    
            errors =generate_form_errors(form,formset=False)   
            context = {
	            "form" : form,
	            "title" : "Error",
                "errors":errors,
                "customers_active":"active"
	            
	        }          
            
        return render(request, 'customers/entry_customer.html', context)

    else: 
        form = CustomerForm()
        
        context = {
            "form" : form,
            "title" : "Create Customer",
            "url" : reverse('customers:create_customer'),
            "redirect" : True,
            "customers_active":"active"
            
        }
        return render(request, 'customers/entry_customer.html', context)
    
    
@login_required
@check_group(['admin'])
def edit_customer(request,pk):
    instance = get_object_or_404(Customer.objects.filter(pk=pk,is_deleted=False))
    
    if request.method == "POST":
        response_data = {}  
        form = CustomerForm(request.POST,instance=instance,request=request,edit=True)
        
        if form.is_valid(): 
            
            #update customer
            data = form.save(commit=False)
            data.updater = request.user
            data.date_updated = datetime.datetime.now()
            data.save()
            
            request.session['message'] = 'Form Edited successfully'
            return HttpResponseRedirect(reverse('customers:view_customer', kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Update Customer",
                "customers_active":"active"
            }          
            
        return render(request, 'customers/entry_customer.html', context)

    else: 
        form = CustomerForm(instance=instance)
        
        context = {
            "form" : form,
            "title" : "Edit customer : " + instance.name,
            "instance" : instance,
            "customers_active":"active"
        }
        return render(request, 'customers/entry_customer.html', context)

       
@login_required
@check_group(['admin','staff'])
def view_customers(request):
    current_shop = get_current_shop(request)
    instances = Customer.objects.filter(shop=current_shop,is_deleted=False)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    title = "Customers"


    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Customers (%s)" % query
        instances = instances.filter(Q(name__icontains=query)|Q(customer_id__icontains=query)|Q(phone__icontains=query)|Q(email__icontains=query))

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
        "customers_active":"active" 
    }
    return render(request,'customers/view_customers.html',context) 


@login_required
@check_group(['admin','staff'])
def view_customer(request,pk):
    instance = get_object_or_404(Customer.objects.filter(pk=pk,is_deleted=False))
    
    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    context = {
        "instance" : instance,
        "title" : "Customer : " + str(instance.name),
        "message" : message,
        "customers_active":"active"
    }
    return render(request,'customers/view_customer.html',context)


@login_required
@check_group(['admin'])
def delete_customer(request,pk):
    instance = get_object_or_404(Customer.objects.filter(pk=pk))
    Customer.objects.filter(pk=pk).update(is_deleted=True)
    
    request.session['message'] = 'Successfully Deleted'
    return HttpResponseRedirect(reverse('customers:view_customers'))


@login_required
@check_group(['admin'])
def create_customer_popup(request): 

    if request.method == "POST":
        #get current shop
        shop = get_current_shop(request) 
        form = CustomerForm(request.POST,request=request)
            
        if form.is_valid():

            #create customer_id
            customer_id = 1
            customer_obj = Customer.objects.filter(shop=shop).order_by("-date_added")[:1]
            if customer_obj:
                for customer in customer_obj:
                    customer_id = customer.customer_id + 1
            

            #create farmer
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.customer_id = customer_id
            data.shop = shop
            data.save()
            
            response_data ={
                'status':'true',
                'message': "Customer %s Created Successfully" %(data.name),
            }
            
            response = HttpResponse(json.dumps(response_data), content_type='application/javascript')
            return response
        
        else:    
            errors =generate_form_errors(form,formset=False)   
            response_data = {
                'status':'false',
                'message': errors,
            }
            response = HttpResponse(json.dumps(response_data), content_type='application/javascript')  
            return response