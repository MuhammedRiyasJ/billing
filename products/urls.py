from django.conf.urls import url, include
from django.contrib import admin
import views
from products.autocomplete_light_registry import ProductAutocomplete


urlpatterns = [               
    
    url(r'^create-product/$',views.create_product,name='create_product'),
    url(r'^view-products/$',views.view_products,name='view_products'),
    url(r'^edit-product/(?P<pk>.*)/$',views.edit_product,name='edit_product'),
    url(r'^view-product/(?P<pk>.*)/$',views.view_product,name='view_product'),
    url(r'^delete-product/(?P<pk>.*)/$',views.delete_product,name='delete_product'),
    url(r'^product-autocomplete/$',ProductAutocomplete.as_view(), name='product-autocomplete',),
    url(r'^create-product-popup/$',views.create_product_popup,name='create_product_popup'),
]