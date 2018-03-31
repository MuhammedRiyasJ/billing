from django.conf.urls import url
from django.contrib import admin
import views


urlpatterns = [               
    
    url(r'^view-sale-report/$',views.view_sale_report,name='view_sale_report'),
    url(r'^print-sale-report/$',views.print_sale_report,name='print_sale_report'),

    url(r'^view-purchase-report/$',views.view_purchase_report,name='view_purchase_report'),
    url(r'^print-purchase-report/$',views.print_purchase_report,name='print_purchase_report'),

    url(r'^view-vat/$',views.view_vat,name='view_vat'),
    url(r'^print-vat/$',views.print_vat,name='print_vat'),
    url(r'^export-xlsx/$', views.export_xlsx, name='export_xlsx'),
    url(r'^export-excel/$', views.export_excel, name='export_excel'),
    url(r'^view-excel-report/$', views.view_excel_report, name='view_excel_report'),
]