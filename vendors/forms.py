from django import forms
from django.forms.widgets import TextInput, Textarea, Select
from vendors.models import Vendor
from django.utils.translation import ugettext_lazy as _
from app.functions import get_current_shop


class VendorForm(forms.ModelForm):
    
    class Meta:
        model = Vendor
        exclude = ['id','is_deleted','creator','updater','date_added', 'date_updated','vendor_id','shop','balance']
        widgets = {
            'name': TextInput(attrs={'autofocus':'','class': 'required form-control','placeholder' : 'Name'}),
            'phone': TextInput(attrs={'class': 'required form-control','placeholder' : 'phone'}),
            'email': TextInput(attrs={'class': 'form-control','placeholder' : 'Email'}),
            'address': Textarea(attrs={'class': 'form-control','placeholder' : 'Address'}),
            'state' : Select(attrs={'class':'form-control'}),
            'gstin': TextInput(attrs={'class': 'form-control','placeholder' : 'GSTIN',}),
        }
        error_messages = {
            'name' : {
                'required' : _("Name field is required."),
            },
           
        }

        labels ={
            'gstin':'GSTIN',
        }
         
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.edit = kwargs.pop('edit', False)
        super(VendorForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        request = self.request
        edit = self.edit

        #get current shop
        current_shop = get_current_shop(request)

        vendor = Vendor.objects.filter(name=name,shop=current_shop,is_deleted=False)
        vendor_count = vendor.count()

        if edit and vendor_count==1:
            pass
        elif vendor.exists():
            raise forms.ValidationError(_("Vendor Name already Exists"))

        return self.cleaned_data['name']

    def clean_email(self):
        email = self.request.POST.get('email',None)
        request = self.request
        edit = self.edit

        #get current shop
        current_shop = get_current_shop(request)

        if email:
            vendor = Vendor.objects.filter(email=email,shop=current_shop,is_deleted=False)
            vendor_count = vendor.count()
            
            if edit and vendor_count==1:
                pass
            elif vendor.exists():
                raise forms.ValidationError(_("Email already Exists"))

        return self.cleaned_data['email']

    def clean_phone(self):
        phone = self.request.POST.get('phone',None)
        request = self.request
        edit = self.edit

        #get current shop
        current_shop = get_current_shop(request)

        if phone:
            vendor = Vendor.objects.filter(phone=phone,shop=current_shop,is_deleted=False)

            vendor_count = vendor.count()
            
            if edit and vendor_count==1:
                pass
            elif vendor.exists():
                raise forms.ValidationError(_("Phone number already Exists"))

        return self.cleaned_data['phone']  