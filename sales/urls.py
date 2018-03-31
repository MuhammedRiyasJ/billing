from django.conf.urls import url, include
from django.contrib import admin
import views


urlpatterns = [
    url(r'^create-sale/$', views.create_sale, name='create_sale'),
    url(r'^view-sale/(?P<pk>.*)/$', views.view_sale, name='view_sale'),
    url(r'^edit-sale/(?P<pk>.*)/$', views.edit_sale, name='edit_sale'),
    url(r'^view-sales/$', views.view_sales, name='view_sales'),
    url(r'^delete-sale/(?P<pk>.*)/$', views.delete_sale, name='delete_sale'),
    url(r'^print-sale-8b/(?P<pk>.*)/$', views.print_sale_8b, name='print_sale_8b'),
    url(r'^print-sale-8/(?P<pk>.*)/$', views.print_sale_8, name='print_sale_8'),

    url(r'^get-unit-price/$', views.get_unit_price, name='get_unit_price'),
]
