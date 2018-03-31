from django.conf.urls import url
from users import views

urlpatterns =[
	url(r'^create-user/$',views.create_user,name='create_user'),
	url(r'^edit-user/(?P<pk>.*)/$',views.edit_user,name='edit_user'),
	url(r'^view-user/(?P<pk>.*)/$',views.view_user,name='view_user'),
	url(r'^view-users/$',views.view_users,name='view_users'),
	url(r'^delete-user/(?P<pk>.*)/$',views.delete_user,name='delete_user'),
	url(r'^change-password/(?P<pk>.*)/$',views.change_password,name='change_password'),

	url(r'^change-shop/$',views.change_shop,name='change_shop'),
]