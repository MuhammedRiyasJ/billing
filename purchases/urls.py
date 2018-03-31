from django.conf.urls import url, include
from django.contrib import admin
import views


urlpatterns = [
    url(r'^create-purchase/$', views.create_purchase, name='create_purchase'),
    url(r'^view-purchase/(?P<pk>.*)/$', views.view_purchase, name='view_purchase'),
    url(r'^edit-purchase/(?P<pk>.*)/$', views.edit_purchase, name='edit_purchase'),
    url(r'^purchases/$', views.view_purchases, name='view_purchases'),
    url(r'^delete-purchase/(?P<pk>.*)/$', views.delete_purchase, name='delete_purchase'),

    url(r'^get-input-tax/$', views.get_input_tax, name='get_input_tax'),
       
]