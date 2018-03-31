from users.models import Profile
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from app.models import Notification


def main_context(request):

	admin = False

	try:
		instance = get_object_or_404(Profile.objects.filter(user=request.user))
		current_shop = instance.current_shop
		user_shops = instance.shops.filter(is_deleted=False)

		if instance.user_type =='admin':
			admin = True
		else:
			pass

	except:
		current_shop = None
		user_shops = None
		instance = None

	try:
		if admin:
			notification_count = Notification.objects.filter(is_deleted=False,is_read=False,shop=current_shop).count()
		else:
			notification_count = Notification.objects.filter(is_deleted=False,is_read=False,is_cheque=False,shop=current_shop).count()
	except:
		notification = None
		notification_count = 0

	context={
		'current_user_profile': instance,
		'current_shop': current_shop,
		"user_shops":user_shops,
		'notification_count' : notification_count,
		'change_shop_url': reverse('users:change_shop'),
		'admin': admin
	}
	return context