from django.conf.urls import url, include
from django.contrib import admin
import views


urlpatterns = [
    url(r'^create-shop/$', views.create_shop, name='create_shop'),
    url(r'^view-shop/(?P<pk>.*)/$', views.view_shop, name='view_shop'),
    url(r'^edit-shop/(?P<pk>.*)/$', views.edit_shop, name='edit_shop'),
    url(r'^view-shops/$', views.view_shops, name='view_shops'),
    url(r'^delete-shop/(?P<pk>.*)/$', views.delete_shop, name='delete_shop'),  

]