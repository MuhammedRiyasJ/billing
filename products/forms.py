from django import forms
from django.forms.widgets import TextInput, Select, Textarea,CheckboxInput
from django.utils.translation import ugettext_lazy as _
from products.models import Product
from app.functions import get_current_shop


class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        exclude = ['id','is_deleted','creator','updater','date_added','date_updated','shop','product_id','stock','untaxed']
        widgets = {
            'hsn_code': TextInput(attrs={'autofocus':'','class': 'form-control','placeholder' : 'HSN Code'}),
            'name': TextInput(attrs={'autofocus':'','class': 'form-control','placeholder' : '* Name'}),
            'unit_price': TextInput(attrs={'class': 'form-control','placeholder' : '* Unit Price'}),
            'input_gst':  TextInput(attrs={'class': 'form-control','placeholder' : '* Input GST(%)'}),
            'output_gst':  TextInput(attrs={'class': 'form-control','placeholder' : '* Output GST(%)'}),
        }
        error_messages = {
            'name' : {
                'required' : _("Name field is required."),
            },
            'unit_price' : {
                'required' : _("Unit Price field is required."),
            },
            'input_gst' : {
                'required' : _("Input GST field is required."),
            },
            'output_gst' : {
                'required' : _("Output GST field is required."),
            }
                          
        }
        
        labels={
            'unit_price': 'Unit Sales Price',
            'input_gst' : 'Input GST(%)',
            'output_gst': 'Output GST(%)',

        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.edit = kwargs.pop('edit', False)
        super(ProductForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        request = self.request
        edit = self.edit

        #get current shop
        current_shop = get_current_shop(request)

        product = Product.objects.filter(name=name,shop=current_shop,is_deleted=False)
        product_count = product.count()
        
        if edit and product_count==1:
            pass
        elif product.exists():
            raise forms.ValidationError(_("Product already Exists"))

        return self.cleaned_data['name']
        
        