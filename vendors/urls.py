from django.conf.urls import url, include
from django.contrib import admin
import views
from vendors.autocomplete_light_registry import VendorAutocomplete


urlpatterns = [
    url(r'^create-vendor/$', views.create_vendor, name='create_vendor'),
    url(r'^view-vendor/(?P<pk>.*)/$', views.view_vendor, name='view_vendor'),
    url(r'^edit-vendor/(?P<pk>.*)/$', views.edit_vendor, name='edit_vendor'),
    url(r'^view-vendors/$', views.view_vendors, name='view_vendors'),  
    url(r'^delete-vendor/(?P<pk>.*)/$', views.delete_vendor, name='delete_vendor'),
    url(r'^vendor-autocomplete/$',VendorAutocomplete.as_view(), name='vendor-autocomplete',),
    url(r'^create-vendor-popup/$', views.create_vendor_popup, name='create_vendor_popup'),
]