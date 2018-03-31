from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.db.models import Q
from shops.forms import ShopForm
from shops.models import Shop
from users.models import Profile
from app.functions import generate_form_errors
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
@check_group(['superuser'])
def create_shop(request):     
    if request.method == "POST":
        form = ShopForm(request.POST)
                
        if form.is_valid(): 

            #generate auto id
            shop_id = 1
            shop_obj=  Shop.objects.all().order_by("-date_added")[:1]
            if  shop_obj:
                for shop in shop_obj:
                    shop_id = shop.shop_id+ 1
       
            #create shop
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.shop_id = shop_id
            data.save()

            profiles = Profile.objects.filter(user_type='admin')

            for profile in profiles:
                profile.shops.add(data.pk)
            
            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('shops:view_shop', kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Create Shop",
                "errors": errors,
                "shops_active":"active"
            }          
            
            return render(request, 'shops/entry_shop.html', context)

    else: 
        form = ShopForm()
        
        context = {
            "form" : form,
            "title" : "Create Shop",
            "url": reverse('shops:create_shop'),
            "shops_active":"active"
        }
        return render(request, 'shops/entry_shop.html', context)


@login_required
@check_group(['superuser'])
def edit_shop(request,pk):
    instance = get_object_or_404(Shop.objects.filter(pk=pk,is_deleted=False))     
    if request.method == "POST":
        form = ShopForm(request.POST,instance=instance)
                
        if form.is_valid(): 

            #edit shop
            data = form.save(commit=False)
            data.updater = request.user
            data.date_updated = datetime.datetime.now()
            data.save()
            
            request.session['message'] = 'Form Edited successfully'
            return HttpResponseRedirect(reverse('shops:view_shop', kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Edit Shop",
                "errors": errors,
                "shops_active":"active"
            }          
            
        return render(request, 'shops/entry_shop.html', context)

    else: 
        form = ShopForm(instance=instance)
        
        context = {
            "form" : form,
            "title" : "Edit Shop : "+ instance.name,
            "url": reverse('shops:edit_shop', kwargs = {'pk' : instance.pk}),
            "shops_active":"active"
        }
        return render(request, 'shops/entry_shop.html', context)


@login_required
@check_group(['admin','superuser','staff'])
def view_shop(request,pk):

    instance = get_object_or_404(Shop.objects.filter(pk=pk))

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    context={
     'instance':instance,
     'title':'Shop : '+instance.name,
     'message': message,
     "shops_active":"active"
    }
    return render(request,'shops/view_shop.html',context)


@login_required
@check_group(['superuser'])
def view_shops(request):
    instances = Shop.objects.filter(is_deleted=False)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    title = "Shops"

    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Shops (%s)" % query
        instances = instances.filter(Q(shop_id__icontains=query)|Q(name__icontains=query)|Q(location__icontains=query))

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
        "message":message,
        "shops_active":"active"
    }
    return render(request,'shops/view_shops.html',context)


@login_required
@check_group(['superuser'])
def delete_shop(request,pk):

    instance = get_object_or_404(Shop.objects.filter(pk=pk))
    Shop.objects.filter(pk=pk).update(is_deleted=True)
    
    request.session['message']='Shop Deleted Successfully'
    return HttpResponseRedirect(reverse('shops:view_shops'))


    