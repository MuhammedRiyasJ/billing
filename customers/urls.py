from django.conf.urls import url, include
from django.contrib import admin
import views
from customers.autocomplete_light_registry import CustomerAutocomplete
from customers.models import Customer
from django.views import generic


urlpatterns = [               
    
    url(r'^create-customer/$',views.create_customer,name='create_customer'),
    url(r'^view-customers/$',views.view_customers,name='view_customers'),
    url(r'^edit-customer/(?P<pk>.*)/$',views.edit_customer,name='edit_customer'),
    url(r'^view-customer/(?P<pk>.*)/$',views.view_customer,name='view_customer'),
    url(r'^delete-customer/(?P<pk>.*)/$',views.delete_customer,name='delete_customer'),
    url(r'^customer-autocomplete/$',CustomerAutocomplete.as_view(), name='customer-autocomplete',),
    url(r'^create-customer-popup/$',views.create_customer_popup,name='create_customer_popup'),
]