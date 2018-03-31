from django import forms
from sales.models import Sale, SaleProduct
from django.forms.widgets import TextInput, Select, DateTimeInput
from django.utils.translation import ugettext_lazy as _
from dal import autocomplete


class SaleForm(forms.ModelForm):
    
    class Meta:
        model = Sale
        exclude = ['id','creator','updater','is_deleted','sale_id','date_added','date_updated','shop']
        widgets = {
            'date' : DateTimeInput(attrs={'placeholder': 'Enter date','class':'required form-control'}),
            'customer': autocomplete.ModelSelect2(url='customers:customer-autocomplete',attrs={'data-placeholder': 'Select Customer','data-minimum-input-length': 1}),
            'sale_type' : Select(attrs={'class':'form-control'}),
        }
        error_messages = {
            'date' : {
                'required' : _("Date field is required."),
            },        
        }


class SaleProductForm(forms.ModelForm):
    
    class Meta:
        model = SaleProduct
        exclude = ['is_deleted','sale']
        widgets = {
            'product': autocomplete.ModelSelect2(url='products:product-autocomplete',attrs={'data-placeholder': '*Select Product','data-minimum-input-length': 1}),
            'unit_price' : TextInput(attrs={'placeholder': '*Enter unit price(inc. tax)','label': '*Unit price','class':'required form-control'}),
            'output_gst' : TextInput(attrs={'placeholder': 'Output GST','class': 'required form-control'}),
            'quantity' : TextInput(attrs={'placeholder': '*Enter quantity','class':'required form-control'}),
            'offer' : TextInput(attrs={'placeholder': 'Enter Discount','class':'required form-control'}),
            'tax_amount' : TextInput(attrs={'placeholder': 'Tax amount','class':'required form-control'}),
            'amount' : TextInput(attrs={'placeholder': 'Enter amount','class':'required form-control'}),
            'total_amount' : TextInput(attrs={'placeholder': 'Enter total amount','class':'required form-control'}),
        }
        error_messages = {
            'product' : {
                'required' : _("Product field is required."),
            },
            'unit_price' : {
                'required' : _("Unit Price field is required."),
            },
            'quantity' : {
                'required' : _("Quantity field is required."),
            },             
        }
