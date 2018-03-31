from django.conf.urls import url, include
from django.contrib import admin
import views
from django.views import generic


urlpatterns = [               
    
    url(r'^create-expense/$',views.create_expense,name='create_expense'),
    url(r'^view-expenses/$',views.view_expenses,name='view_expenses'),
    url(r'^edit-expense/(?P<pk>.*)/$',views.edit_expense,name='edit_expense'),
    url(r'^view-expense/(?P<pk>.*)/$',views.view_expense,name='view_expense'),
    url(r'^delete-expense/(?P<pk>.*)/$',views.delete_expense,name='delete_expense'),
]