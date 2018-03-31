from django.shortcuts import render,get_object_or_404
from users.forms import UserForm, EditUserForm, ProfileForm, ChangeShopForm
import datetime
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from users.models import Profile
from django.contrib.auth.models import User
from shops.models import Shop
from app.functions import generate_form_errors
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm


# Create your views here.
@login_required
@check_group(['superuser'])
def create_user(request):

	if request.method == 'POST':


		form = UserForm(request.POST)
		profile = ProfileForm(request.POST)

		if form.is_valid() and profile.is_valid():

			shops = profile.cleaned_data['shops']

			#save form
			user_data = form.save(commit=False)
			user_data.save()

			#save profile form
			profile_data = profile.save(commit=False)
			profile_data.creator = request.user
			profile_data.updater = request.user
			profile_data.user = user_data
			profile_data.current_shop = shops[0]
			profile_data.save()
			profile.save_m2m()

			request.session['message']='User Created Successfully'
			return HttpResponseRedirect(reverse('users:view_user', kwargs={'pk': profile_data.pk}))

		else:
			errors = generate_form_errors(form,formset=False)
			errors += generate_form_errors(profile,formset=False)

			context ={
				'form':form,
				'profile':profile,
				'title':'Create User',
				'message':'Form Validation Error',
				"errors": errors,
				'url': reverse('users:create_user'),
				"users_active":"active"
			}
			return render(request,'users/entry_user.html',context)

	else:
		form = UserForm()
		profile = ProfileForm()
		context ={
			"form": form,
			"profile":profile,
			"title": "Create User",
			'url': reverse('users:create_user'),
			"users_active":"active"
		}
		return render(request,'users/entry_user.html',context)


@login_required
@check_group(['superuser'])
def edit_user(request,pk):
	instance = get_object_or_404(Profile.objects.filter(pk=pk,is_deleted=False))

	if request.method == 'POST':
		form = EditUserForm(request.POST,instance=instance.user)
		profile = ProfileForm(request.POST,instance = instance)

		if form.is_valid() and profile.is_valid():

			#save auth user
			user_data = form.save(commit=False)
			user_data.save()

			#save profile
			profile_data = profile.save(commit=False)
			profile_data.updater = request.user
			profile_data.date_updated = datetime.datetime.now()
			profile_data.save()
			profile.save_m2m()
			
			request.session['message']='User Successfully Edited'
			return HttpResponseRedirect(reverse('users:view_user', kwargs={'pk': instance.pk}))
			
		else:
			errors =generate_form_errors(form,formset=False)
			errors += generate_form_errors(profile,formset=False)
			context={
				'message': 'Form Validation Error',
				'title': 'Edit Form',
				'form':form,
				'profile':profile,
				"errors": errors,
				"users_active":"active",
				'url':reverse('users:edit_user', kwargs={'pk': instance.pk}),
			}
			return render(request,'users/entry_user.html',context)

	else:

		form = EditUserForm(instance=instance.user)
		profile = ProfileForm(instance=instance)

		context = {
			'title':'Edit User'+ instance.user.username,
			'form': form,
			'profile':profile,
			'instance': instance,
			'url':reverse('users:edit_user', kwargs={'pk': instance.pk}),
			"users_active":"active"
		}
		return render(request,'users/entry_user.html',context)


@login_required
@check_group(['admin','superuser'])
def view_user(request,pk):
	instance = get_object_or_404(Profile.objects.filter(pk=pk,is_deleted=False))

	try:
		message = request.session['message']
		del request.session['message']
	except KeyError:
		message = None

	context ={
		'title':'View User : '+ instance.user.username,
		'instance': instance,
		'message': message,
		"users_active":"active"
	}
	return render(request,'users/view_user.html',context)


@login_required
@check_group(['admin','superuser'])
def view_users(request):
	instances = Profile.objects.filter(is_deleted=False)

	try:
		message = request.session['message']
		del request.session['message']
	except KeyError:
		message = None

	title = 'View Users'

	#filter by query
	query = request.GET.get("q")
	if query:
		title = "View Users (%s)" % query
		instances = instances.filter(Q(user__username__icontains=query)|Q(user_type__icontains=query))

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

	context ={
		'title':title,
		'instances':instances,
		'query':query,
		'message':message,
		"users_active":"active"
	}

	return render(request,'users/view_users.html',context)


@login_required
@check_group(['superuser'])
def delete_user(request,pk):
	Profile.objects.filter(pk=pk).update(is_deleted=True)
	profile = get_object_or_404(Profile.objects.filter(pk=pk))
	User.objects.filter(pk=profile.user.pk).update(is_active=False)

	request.session['message']='User Deleted Successfully'
	return HttpResponseRedirect(reverse('users:view_users'))


@login_required
@check_group(['admin','staff'])
def change_shop(request):

    instance = get_object_or_404(Profile.objects.filter(user=request.user))

    if request.method == 'POST':

    	shop_form = ChangeShopForm(request.POST,instance=instance)

    	shop_form.save()

    return HttpResponseRedirect(reverse('dashboard:dashboard'))


@login_required
@check_group(['admin','superuser'])
def change_password(request,pk):

    profile = get_object_or_404(Profile.objects.filter(pk=pk))
    user = get_object_or_404(User.objects.filter(pk=profile.user.pk,is_active=True))

    if request.method == "POST":
        
        change_password_form = SetPasswordForm(user=user,data=request.POST)
        if change_password_form.is_valid():

            change_password_form.save()

            context = {
            	"change_password_form" : change_password_form,
            	"title" : "Change Password: "+ user.username,
            	"message": "Password Changed Succesfully",
            	"instance" : profile,
            }
            return render(request,'includes/change_password.html',context)
        else:
            errors = generate_form_errors(change_password_form,formset=False)     
                    
            context = {
            	"change_password_form" : change_password_form,
            	"title" : "Change Password: "+ user.username,
            	"errors": errors,
            	"instance" : profile,
            } 
                
        return render(request,'includes/change_password.html',context)
    else:
        change_password_form = SetPasswordForm(user=user)  
        context = {
            "change_password_form" : change_password_form,
            "title" : "Change Password: "+ user.username,
            "instance" : profile,
        }
        return render(request, 'includes/change_password.html', context)

