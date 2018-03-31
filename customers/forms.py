from django import forms
from django.forms.widgets import TextInput, Select, Textarea,DateInput
from django.utils.translation import ugettext_lazy as _
from customers.models import Customer
from app.functions import get_current_shop


class CustomerForm(forms.ModelForm):
    
    class Meta:
        model = Customer
        exclude = ['id','is_deleted','creator','updater','date_added','date_updated', 'shop','customer_id','balance','cst']
        widgets = {
            'name': TextInput(attrs={'autofocus':'','class': 'required form-control','placeholder' : '*Name'}),
            'phone': TextInput(attrs={'class': 'form-control','placeholder' : 'Phone'}),
            'email': TextInput(attrs={'class': 'form-control','placeholder' : 'Email'}),
            'details': Textarea(attrs={'class': 'form-control','placeholder' : 'Details'}),
            'gstin': TextInput(attrs={'class': 'form-control','placeholder' : 'GSTIN',}),
            'state' : Select(attrs={'class':'form-control'}),
        }
        error_messages = {
            'name' : {
                'required' : _("Name field is required."),
            },
            'phone' : {
                'required' : _("Phone field is required."),
            },
            'email' : {
                'required' : _("Email field is required."),
            },
            'details' : {
                'required' : _("Details field is required."),
            },
        }

        labels ={
            'gstin':'GSTIN',
        }
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.edit = kwargs.pop('edit', False)
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['state'].empty_label = None

    def clean_name(self):
        name = self.cleaned_data['name']
        request = self.request
        edit = self.edit

        #get current shop
        current_shop = get_current_shop(request)

        customer = Customer.objects.filter(name=name,shop=current_shop,is_deleted=False)
        customer_count = customer.count()

        if edit and customer_count==1:
            pass
        elif customer.exists():
            raise forms.ValidationError(_("Customer already Exists"))

        return self.cleaned_data['name']

    def clean_email(self):
        email = self.request.POST.get('email',None)
        request = self.request
        edit = self.edit

        #get current shop
        current_shop = get_current_shop(request)

        if email:
            customer = Customer.objects.filter(email=email,shop=current_shop,is_deleted=False)
            customer_count = customer.count()

            if edit and customer_count==1:
                pass
            elif customer.exists():
                raise forms.ValidationError(_("Email already Exists"))

        return self.cleaned_data['email']

    def clean_phone(self):
        phone = self.request.POST.get('phone',None)
        request = self.request
        edit = self.edit

        print str(phone)+"jaseemm"

        #get current shop
        current_shop = get_current_shop(request)

        if phone:
            customer = Customer.objects.filter(phone=phone,shop=current_shop,is_deleted=False)
            customer_count = customer.count()

            if edit and customer_count==1:
                pass
            elif customer.exists():
                raise forms.ValidationError(_("Phone number already Exists"))

        return self.cleaned_data['phone']  