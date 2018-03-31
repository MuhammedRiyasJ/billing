from django.conf.urls import url
import views


urlpatterns=[
	url(r'^$',views.dashboard,name="dashboard"),
	url(r'^view-notifications/$',views.view_notifications,name='view_notifications'),
	url(r'^mark-as-read/(?P<pk>.*)/$',views.mark_as_read,name='mark_as_read'),
	url(r'^mark-as-not-read/(?P<pk>.*)/$',views.mark_as_not_read,name='mark_as_not_read'),
	url(r'^search-result/$',views.search_result,name='search_result'),
	url(r'^mark-as-deleted/(?P<pk>.*)/$',views.mark_as_deleted,name='mark_as_deleted'),
]