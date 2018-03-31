from functools import wraps
from django.core.exceptions import PermissionDenied
from users.models import Profile


def check_group(group_list):
	def _check_group(view_func):
		@wraps(view_func)
		def wrapper(request,*args,**kwargs):

			try:
				user_type = Profile.objects.get(user=request.user).user_type

			except:

				if request.user.is_superuser:

					user_type = 'superuser'

				else:

					user_type = None

			if user_type in group_list:

				return view_func(request, *args, **kwargs)

			else:
				raise PermissionDenied

		return wrapper
		
	return _check_group




