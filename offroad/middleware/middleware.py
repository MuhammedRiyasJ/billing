from cheques.models import Cheque
import datetime
from app.functions import create_cheque_notification
from django.shortcuts import render, get_object_or_404
from datetime import timedelta
from app.functions import get_current_shop



def cheque_notification_middleware(get_response):

	def middleware(request):
		if not request.user.is_superuser:

			current_shop = get_current_shop(request) 
			
			if Cheque.objects.filter(is_notified=False,is_deleted=False,shop=current_shop).exists():
				instances = Cheque.objects.filter(is_notified=False,is_deleted=False,shop=current_shop)
				for instance in instances:
					date = instance.date
					today = datetime.datetime.now()
					limit_date = date - today

					if limit_date <= timedelta(days=4):
						create_cheque_notification(instance,current_shop)
						Cheque.objects.filter(is_deleted=False).update(is_notified=True)

		response = get_response(request)

		return response

	return middleware