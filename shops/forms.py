from django import forms
from django.forms.widgets import TextInput, Textarea
from shops.models import Shop
from django.utils.translation import ugettext_lazy as _


class ShopForm(forms.ModelForm):
    
    class Meta:
        model = Shop
        exclude = ['id','is_deleted','creator','updater','date_added', 'date_updated','shop_id']
        widgets = {
            'name': TextInput(attrs={'autofocus':'','class': 'form-control','placeholder' : 'Name'}),
            'location': TextInput(attrs={'class': 'form-control','placeholder' : 'Location'}),
            'contact_no': TextInput(attrs={'class': 'form-control','placeholder' : 'Contact No.'}),
            'gstin': TextInput(attrs={'class': 'required form-control','placeholder' : 'GSTIN'}),
            'cst':TextInput(attrs={'class': 'required form-control','placeholder' : 'CST'}),
        }