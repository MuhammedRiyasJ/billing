from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.conf.urls import (
handler400, handler403, handler404, handler500
)


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^',include('app.urls',namespace='dashboard')),
    url(r'^users/',include('users.urls',namespace='users')),
    url(r'^shops/',include('shops.urls',namespace='shops')),
    url(r'^products/',include('products.urls',namespace='products')),
    url(r'^customers/',include('customers.urls',namespace='customers')),
    url(r'^purchases/',include('purchases.urls',namespace='purchases')),
    url(r'^vendors/',include('vendors.urls',namespace='vendors')),
    url(r'^sales/',include('sales.urls',namespace='sales')),
    url(r'^reports/',include('reports.urls',namespace='reports')),
    url(r'^app/',include('app.urls',namespace='app')),
    url(r'^expense/',include('expense.urls',namespace='expense')),
    url(r'^cheque-details/',include('cheques.urls',namespace='cheques')),
    
    url(r'^static/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_FILE_ROOT,}),
    url(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT,}),
]

handler400 = "app.views.handler400"
handler403 = "app.views.handler403"
handler404 = "app.views.handler404"
handler500 = "app.views.handler500"