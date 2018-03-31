from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.db.models import Q
from vendors.forms import VendorForm
from vendors.models import Vendor
from app.functions import get_current_shop, generate_form_errors
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



@login_required
@check_group(['admin'])
def create_vendor(request):
    if request.method == "POST":
        form = VendorForm(request.POST,request=request)
        current_shop = get_current_shop(request)

        if form.is_valid():
            #generate auto id
            vendor_id = 1 
            vendor_obj= Vendor.objects.filter(shop=current_shop).order_by("-date_added")[:1]    
            if vendor_obj:
                for vendor in vendor_obj:
                    vendor_id = vendor.vendor_id+1


            #create vendor
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.vendor_id = vendor_id
            data.shop = current_shop
            data.save()


            request.session['message'] = 'Form Submitted Successfully'
            return HttpResponseRedirect(reverse('vendors:view_vendor',kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Create Vendor",
                "errors" : errors,
                "vendors_active":"active"
            }
            return render(request,'vendors/entry_vendor.html',context)

    else:
    	form = VendorForm()


    	context = {
    		"form" : form,
    		"title" : "Create Vendor",
    		"url" : reverse('vendors:create_vendor'),
            "vendors_active":"active"
    	}

    	return render(request,'vendors/entry_vendor.html',context)


@login_required
@check_group(['admin'])
def edit_vendor(request,pk):
    instance = get_object_or_404(Vendor.objects.filter(pk=pk,is_deleted=False))     
    if request.method == "POST":
        form = VendorForm(request.POST,instance=instance,request=request,edit=True)
                
        if form.is_valid(): 

            #edit vendor
            data = form.save(commit=False)
            data.updater = request.user
            data.date_updated = datetime.datetime.now()
            data.save()
            
            request.session['message'] = 'Form Edited successfully'
            return HttpResponseRedirect(reverse('vendors:view_vendor', kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Edit vendor",
                "errors" : errors,
                "vendors_active":"active"
            }          
            
        return render(request, 'vendors/entry_vendor.html', context)

    else: 
        form = VendorForm(instance=instance)
        
        context = {
            "form" : form,
            "title" : "Edit Vendor : "+ instance.name,
            "url": reverse('vendors:edit_vendor', kwargs = {'pk' : instance.pk}),
            "vendors_active":"active"
        }
        return render(request, 'vendors/entry_vendor.html', context)


@login_required
@check_group(['admin'])
def view_vendor(request,pk):

    instance = get_object_or_404(Vendor.objects.filter(pk=pk))

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
   		message = None

    context={
   		'instance':instance,
   		'title':'Vendor '+instance.name,
   		'message': message,
        "vendors_active":"active"
    }
    return render(request,'vendors/view_vendor.html',context)


@login_required
@check_group(['admin'])
def view_vendors(request):
    current_shop = get_current_shop(request)
    instances = Vendor.objects.filter(is_deleted=False,shop=current_shop)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    title = "Vendors"

    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Vendors (%s)" % query
        instances = instances.filter(Q(name__icontains=query)|Q(phone__icontains=query)|Q(email__icontains=query)|Q(address__icontains=query))

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
        "title" : title,
        "instances" : instances,
        "message":message,
        'query':query,
        "vendors_active":"active"
    }
    return render(request,'vendors/view_vendors.html',context)


@login_required
@check_group(['admin'])
def delete_vendor(request,pk):
    instance = get_object_or_404(Vendor.objects.filter(pk=pk))
    Vendor.objects.filter(pk=pk).update(is_deleted=True)
    
    request.session['message'] = 'Successfully Deleted'
    return HttpResponseRedirect(reverse('vendors:view_vendors'))


@login_required
@check_group(['admin'])
def create_vendor_popup(request):

     if request.method == "POST":
        form = VendorForm(request.POST,request=request)
        current_shop = get_current_shop(request)

        if form.is_valid():
            #generate auto id
            vendor_id = 1 
            vendor_obj= Vendor.objects.filter(shop=current_shop).order_by("-date_added")[:1]
            if vendor_obj:
                for vendor in vendor_obj:
                    vendor_id = vendor.vendor_id+1


            #create vendor
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.vendor_id = vendor_id
            data.shop = current_shop
            data.save()


            response_data = {
                'status':'true',
                'message': "Vendor %s Created Successfully" %(data.name),
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