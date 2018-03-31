from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect
import json
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from expense.forms import ExpenseForm
from expense.models import Expense
from app.functions import get_current_shop, generate_form_errors
from django.contrib.auth.decorators import login_required
from app.decorators import check_group
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
@check_group(['admin'])
def create_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
            
        if form.is_valid():

            #get current shop
            shop = get_current_shop(request)
            
            #create farmer
            data = form.save(commit=False)
            data.creator = request.user
            data.updater = request.user
            data.shop = shop
            data.save()
            
            request.session['message'] = 'Form Submitted successfully'
            return HttpResponseRedirect(reverse('expense:view_expense', kwargs = {'pk' : data.pk}))
        
        else:    
            errors =generate_form_errors(form,formset=False)   
            context = {
	            "form" : form,
	            "title" : "Error",
                "errors":errors,
                "expenses_active":"active"
	            
	        }          
            
        return render(request, 'expense/entry_expense.html', context)

    else: 
        form = ExpenseForm()
        
        context = {
            "form" : form,
            "title" : "Create Expense",
            "url" : reverse('expense:create_expense'),
            "redirect" : True,
            "expenses_active":"active"
            
        }
        return render(request, 'expense/entry_expense.html', context)
    
    
@login_required
@check_group(['admin'])
def edit_expense(request,pk):
    instance = get_object_or_404(Expense.objects.filter(pk=pk,is_deleted=False))
    
    if request.method == "POST":
        response_data = {}  
        form = ExpenseForm(request.POST,instance=instance)
        
        if form.is_valid(): 
            
            #update expense
            data = form.save(commit=False)
            data.updater = request.user
            data.date_updated = datetime.datetime.now()
            data.save()
            
            request.session['message'] = 'Form Edited successfully'
            return HttpResponseRedirect(reverse('expense:view_expense', kwargs = {'pk' : data.pk}))
        else:
            errors =generate_form_errors(form,formset=False)
            context = {
                "form" : form,
                "title" : "Update Expense",
                "expenses_active":"active"
            }          
            
        return render(request, 'expense/entry_expense.html', context)

    else: 
        form = ExpenseForm(instance=instance)
        
        context = {
            "form" : form,
            "title" : "Edit expense",
            "instance" : instance,
            "expenses_active":"active"
        }
        return render(request, 'expense/entry_expense.html', context)

       
@login_required
@check_group(['admin'])
def view_expenses(request):
    current_shop = get_current_shop(request)
    instances = Expense.objects.filter(shop=current_shop,is_deleted=False)

    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    title = "Expenses"


    #filter by query
    query = request.GET.get("q")
    if query:
        title = "Expense (%s)" % query
        try:
            date_query = datetime.datetime.strptime(query,"%d-%m-%y")
        except:
            date_query = query
        instances = instances.filter(Q(date__icontains=date_query)|Q(amount__icontains=query)|Q(description__icontains=query))

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
        "expenses_active":"active" 
    }
    return render(request,'expense/view_expenses.html',context) 


@login_required
@check_group(['admin'])
def view_expense(request,pk):
    instance = get_object_or_404(Expense.objects.filter(pk=pk,is_deleted=False))
    
    try:
        message = request.session['message']
        del request.session['message']
    except KeyError:
        message = None

    context = {
        "instance" : instance,
        "title" : "Expense : " + str(instance.amount),
        "message" : message,
        "expenses_active":"active"
    }
    return render(request,'expense/view_expense.html',context)


@login_required
@check_group(['admin'])
def delete_expense(request,pk):
    instance = get_object_or_404(Expense.objects.filter(pk=pk))
    Expense.objects.filter(pk=pk).update(is_deleted=True)
    
    request.session['message'] = 'Successfully Deleted'
    return HttpResponseRedirect(reverse('expense:view_expenses'))
