from django import forms
from purchases.models import Purchase, PurchaseProduct
from django.forms.widgets import TextInput, Select, DateTimeInput
from django.utils.translation import ugettext_lazy as _
from dal import autocomplete


class PurchaseForm(forms.ModelForm):
    
    class Meta:
        model = Purchase
        exclude = ['creator','updater','is_deleted','purchase_id','date_added','date_updated','shop']
        widgets = {
            'date' : DateTimeInput(attrs={'placeholder': '*Enter date','class':'required form-control'}),
            'vendor': autocomplete.ModelSelect2(url='vendors:vendor-autocomplete',attrs={'data-placeholder': 'Select Vendor','data-minimum-input-length': 1}),
            'purchase_date' : DateTimeInput(attrs={'placeholder': 'Enter date','class':'form-control'}),
            'invoice_no':TextInput(attrs={'placeholder': 'Invoice No.','class':'form-control'}),
            'other_charges':TextInput(attrs={'placeholder': 'Other Charges','class':'form-control'}),
            'final_total':TextInput(attrs={'placeholder': 'Sub Total','class':'form-control'}),
            'paid' : TextInput(attrs={'placeholder': 'Paid','class':'required form-control'}),
            'balance' : TextInput(attrs={'placeholder': 'Balance','class':'required form-control'}),
            'purchase_type' : Select(attrs={'class':'form-control'}),
        }
        error_messages = {
            'date' : {
                'required' : _("Date field is required."),
            },
            'vendor' : {
                'required' : _("Vendor field is required."),
            },
            'paid' : {
                'required' : _("Paid field is required."),
            },
            'balance' : {
                'required' : _("Balance field is required."),
            },
                          
        }

class PurchaseProductForm(forms.ModelForm):
    
    class Meta:
        model = PurchaseProduct
        exclude = ['is_deleted', 'purchase']
        widgets = {
            'product': autocomplete.ModelSelect2(url='products:product-autocomplete',attrs={'data-placeholder': '*Select Product','data-minimum-input-length': 1}),
            'unit_cost' : TextInput(attrs={'placeholder': '*Enter unit cost','class':'required form-control'}),
            'input_gst' : TextInput(attrs={'placeholder': 'Input GST','class': 'form-control'}),
            'quantity' : TextInput(attrs={'placeholder': '*Enter quantity','class':'required form-control'}),
            'offer' : TextInput(attrs={'placeholder': 'Enter offer','class':'form-control'}),
            'tax_amount' : TextInput(attrs={'placeholder': 'Tax amount','class':'required form-control'}),
            'amount' : TextInput(attrs={'placeholder': 'Enter amount','class':'required form-control'}),
            'total_amount' : TextInput(attrs={'placeholder': 'Enter total amount','class':'required form-control'}),
        }
        error_messages = {
            'product' : {
                'required' : _("product field is required."),
            },
            'unit_cost' : {
                'required' : _("Unit Cost field is required."),
            },
            'quantity' : {
                'required' : _("Quantity field is required."),
            },           
        }