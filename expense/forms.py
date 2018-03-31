from django import forms
from expense.models import Expense
from django.forms.widgets import TextInput, Select,Textarea, DateTimeInput
from django.utils.translation import ugettext_lazy as _
from dal import autocomplete


class ExpenseForm(forms.ModelForm):
    
    class Meta:
        model = Expense
        exclude = ['creator','updater','is_deleted','date_added','date_updated','shop']
        widgets = {
            'date' : DateTimeInput(attrs={'placeholder': '*Enter date','class':'required form-control'}),
            'amount' : TextInput(attrs={'placeholder': 'Balance','class':'required form-control'}),
            'description': Textarea(attrs={'class': 'form-control','placeholder' : 'Details'}),
        }
        error_messages = {
            'date' : {
                'required' : _("Date field is required."),
            },
            'amount' : {
                'required' : _("Amount field is required."),
            },
                                      
        }